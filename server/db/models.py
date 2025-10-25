from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


