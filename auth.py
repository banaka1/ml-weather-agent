"""
鉴权模块：密码哈希、JWT 签发/校验、当前用户依赖
- bcrypt 加盐哈希
- HS256 JWT，默认 7 天过期
"""
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from models import User

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXP_DAYS = int(os.getenv("JWT_EXP_DAYS", "7"))
ALGORITHM = "HS256"

security = HTTPBearer()


def hash_password(password: str) -> str:
    """bcrypt 加盐哈希（passlib 已停止维护，直接用 bcrypt 库）"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int, username: str) -> str:
    """签发 JWT，sub=user_id"""
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    鉴权依赖：从 Authorization: Bearer <token> 解析并校验用户
    失败统一返回 401
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        username = payload.get("username")
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 token"
        )
    user = (
        db.query(User)
        .filter(User.id == user_id, User.username == username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    return user
