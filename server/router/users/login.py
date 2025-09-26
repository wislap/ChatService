from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr, SecretStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from datetime import datetime, timedelta

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
    print(f"Cleaned up old requests. Current DB size: {len(request_db)}")

# --- API Endpoints ---

@router.post("/user/register1/")
async def register_user1(request: UserRegisterRequest, background_tasks: BackgroundTasks):
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
                <a href="http://localhost:5173/FinnishRegister" class="button">完成注册</a>
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
    
    background_tasks.add_task(fastmail.send_message, message)
    
    request_time = datetime.utcnow()

    # Store the request details in the in-memory database
    request_info = {
        "timestamp": request_time,
        "request_data": {
            "username": request.username,
            "email": request.email
        }
    }
    request_db.append(request_info)
    background_tasks.add_task(cleanup_old_requests)

    return {"message": "User registered successfully", "username": request.username}
