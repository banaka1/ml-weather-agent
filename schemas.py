"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel


# ---- 鉴权 ----
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# ---- 聊天 ----
class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---- 会话 ----
class SessionCreateResponse(BaseModel):
    session_id: str
    title: str


class SessionItem(BaseModel):
    id: str
    title: str
    updated_at: str


class SessionRenameRequest(BaseModel):
    title: str


class OkResponse(BaseModel):
    ok: bool


class MessageItem(BaseModel):
    role: str
    content: str
    ts: str


class ToolCallInfo(BaseModel):
    name: str
    args: dict
    result: str
    ms: int


class ChatResponse(BaseModel):
    reply: str
    intent: str = "chat"
    tools: list[ToolCallInfo] = []
