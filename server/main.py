import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.users.login import router as user_login_router
app = FastAPI()
router = user_login_router
app.include_router(router)

origins = [
    "http://localhost:5173",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=25578)
