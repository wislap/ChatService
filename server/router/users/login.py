from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel, EmailStr, SecretStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from datetime import datetime, timedelta
import hashlib
import secrets
from sqlalchemy.future import select
from aiosmtplib.errors import SMTPResponseException

from db.models import User
from db.database import AsyncSessionLocal
from logger import logger
# In-memory database (a simple list) to store request info
# Each item will be a dictionary: {'timestamp': datetime, 'request_data': dict}
request_db = []

# --- Mail Configuration ---
MAIL_PASSWORD = "aqtztupwyhmpdabi"
conf = ConnectionConfig(
    MAIL_USERNAME="3465467883@qq.com",
    MAIL_PASSWORD=SecretStr(MAIL_PASSWORD),
    MAIL_FROM="3465467883@qq.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.qq.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

router = APIRouter()
fastmail = FastMail(conf)

# --- Pydantic Models ---
class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str


# --- Helper Functions ---
def cleanup_old_requests():
    """Removes requests from the in-memory DB that are older than 24 hours."""
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    # This is a thread-safe way to modify the list in place
    global request_db
    request_db[:] = [req for req in request_db if req['timestamp'] > twenty_four_hours_ago]
    logger.info(f"Cleaned up old requests. Current DB size: {len(request_db)}")

# --- API Endpoints ---


@router.post("/user/register1/")
async def register_user1(request: UserRegisterRequest, background_tasks: BackgroundTasks):
    request_time = datetime.utcnow()
    random_string = secrets.token_urlsafe(32)
    token = hashlib.sha256((request.password + random_string).encode()).hexdigest()
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    verification_url = f"http://localhost:5173/FinnishRegister?token={token}"
    # Store the request details in the in-memory database
    request_info = {
        "timestamp": request_time,
        "verified": False,
        "request_data": {
            "username": request.username,
            "email": request.email,
            "token": token,
            "hashed_password": hashed_password
        }
    }
    request_db.append(request_info)
    """Handles user registration and sends a welcome email."""

    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #42b983;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
            line-height: 1.6;
            color: #333333;
        }}
        .content p {{
            margin: 0 0 20px;
        }}
        .button-container {{
            text-align: center;
            margin-top: 30px;
        }}
        .button {{
            display: inline-block;
            background-color: #42b983;
            color: #ffffff;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #777777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>欢迎加入我们的大家庭！</h1>
        </div>
        <div class="content">
            <p>您好, {request.username}！</p>
            <p>感谢您的注册。请点击下方的按钮来完成您的注册流程并验证您的邮箱地址。</p>
            <div class="button-container">
                <a href="{verification_url}" class="button">完成注册</a>
            </div>
        </div>
        <div class="footer">
            <p>&copy; 2025 ChatService. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    message = MessageSchema(
        subject="测试邮件",
        recipients=[request.email],
        body=html_content,
        subtype=MessageType.html
    )
    try:
        background_tasks.add_task(fastmail.send_message, message)
    except SMTPResponseException as e:
        # 邮件已经发出，但关闭连接时报错，忽略即可
        logger.warning(f"Ignore SMTP quit error: {e}")
    logger.trace(request_db)
    background_tasks.add_task(cleanup_old_requests)

    return {"message": "User registered successfully", "username": request.username}


@router.get("/user/verify-email/")
async def verify_email(token: str):
    """Verifies the user's email using the provided token."""
    logger.info(f"Attempting to verify token: {token}")
    logger.info(f"Current request_db state: {request_db}")

    for req in request_db:
        # Check if the token matches and it has not been verified yet
        if req["request_data"]["token"] == token and not req["verified"]:
            # req["verified"] = True
            
            async with AsyncSessionLocal() as session:
                # 检查是否已存在
                result = await session.execute(
                    select(User).where(User.username == req["request_data"]["username"])
                )
                existing_user = result.scalars().first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="用户已存在")

                new_user = User(
                    username=req["request_data"]["username"],
                    email=req["request_data"]["email"],
                    hashed_password=req["request_data"]["hashed_password"],
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
            logger.success(
                f"Successfully verified email for user: {req['request_data']['username']}")
            return {"message": "Email verified successfully. Your account is now active."}

    # If the loop completes without finding a valid, unverified token
    raise HTTPException(
        status_code=400, detail="Invalid, expired, or already used verification token.")
