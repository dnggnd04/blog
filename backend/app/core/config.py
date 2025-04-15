from dotenv import load_dotenv
from pydantic import BaseSettings
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Settings(BaseSettings):
    PROJECT_NAME = os.getenv("PROJECT_NAME", 'FastAPI Project')
    SECRET_KEY = os.getenv("SECRET_KEY", 'secret')
    API_PREFIX = os.getenv("API_PREFIX", '')
    BACKEND_CORS_ORIGINS = ["*"]
    DATABASE_URL = os.getenv("DATABASE_URL", '')
    ACCESS_TOKEN_EXPIRE_SECONDS : int = 60 * 60 * 24 * 7
    SECURITY_ALGORITHM = 'HS256'
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.ini')

settings = Settings()
