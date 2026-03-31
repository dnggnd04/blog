from fastapi import FastAPI
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware
import uvicorn
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from app.api.api_router import router
from app.api.websocket import websocket_router

def get_application():
    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url='/docs',
        redoc_url='/re-docs',
        description=''
    )
    # Handle CORS Origins parsing safely
    cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(',')] if settings.BACKEND_CORS_ORIGINS else []
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"]
    )
    application.add_middleware(DBSessionMiddleware, db_url=str(os.getenv('DATABASE_URL')))
    application.include_router(router, prefix=settings.API_PREFIX)
    application.include_router(websocket_router, prefix=settings.WEBSOCKET_PREFIX)

    @application.get("/health")
    def health_check():
        return {"status": "ok"}

    return application

app = get_application()
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
