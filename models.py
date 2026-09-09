"""
ORM 模型（对应 sql/init.sql 四张表）
- users / sessions / messages / tool_call_logs
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, BigInteger, DateTime, Text, Enum,
    JSON, Integer, ForeignKey, CHAR,
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(128), nullable=False)  # bcrypt 哈希
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(128), nullable=False, default="新对话")
    is_deleted = Column(Integer, nullable=False, default=0)  # 软删除
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    tool_logs = relationship("ToolCallLog", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(CHAR(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(
        Enum("human", "ai", "tool", "system", name="message_role"), nullable=False
    )
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # 仅 ai 消息可能携带
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="messages")


class ToolCallLog(Base):
    __tablename__ = "tool_call_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(CHAR(36), ForeignKey("sessions.id"), nullable=False)
    tool_name = Column(String(64), nullable=False)
    args = Column(JSON, nullable=False)
    result = Column(Text, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="tool_logs")
