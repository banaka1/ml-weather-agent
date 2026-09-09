"""
数据库连接与会话管理
- SQLAlchemy 2.x 同步引擎（MySQL 5.7 + PyMySQL）
- 启动时校验必需环境变量，缺失 fail-fast
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# FR-7 启动校验必需变量，缺失 fail-fast
_REQUIRED_VARS = [
    "MYSQL_DSN",
    "JWT_SECRET",
    "SILICONFLOW_API_KEY",
    "SILICONFLOW_BASE_URL",
    "SILICONFLOW_MODEL_NAME",
]
_missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
if _missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(_missing)}")

MYSQL_DSN = os.getenv("MYSQL_DSN")

engine = create_engine(
    MYSQL_DSN,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依赖：每次请求获取独立 DB 会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
