from pydantic import BaseSettings
import os
import boto3
from dotenv import load_dotenv

# ── Ưu tiên đọc từ OS environment (Docker Compose inject) ──────
# Nếu chạy local dev (không qua Docker), fallback đọc file .env
# Thứ tự tìm file .env: backend/app/.env → root .env
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
_env_paths = [
    os.path.join(BASE_DIR, 'app', '.env'),   # backend/app/.env (local dev)
    os.path.join(BASE_DIR, '..', '.env'),     # root .env (fallback)
]
for _env_path in _env_paths:
    if os.path.exists(_env_path):
        load_dotenv(_env_path, override=False)  # override=False: OS env thắng .env file
        break


class Settings(BaseSettings):
    PROJECT_NAME = os.getenv("PROJECT_NAME", 'FastAPI Project')
    SECRET_KEY = os.getenv("SECRET_KEY", 'secret')
    API_PREFIX = os.getenv("API_PREFIX", '')
    WEBSOCKET_PREFIX = os.getenv("WEBSOCKET_PREFIX", '')
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", '')
    DATABASE_URL = os.getenv("DATABASE_URL", '')
    ACCESS_TOKEN_EXPIRE_SECONDS : int = 60 * 3
    REFRESH_TOKEN_EXPIRE_SECONDS : int = 60 * 60 * 24 * 7
    SECURITY_ALGORITHM = 'HS256'
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.ini')

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", '')
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", '')
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", '')
    AWS_REGION = os.getenv("AWS_REGION", '')

settings = Settings()

s3_avatar = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

