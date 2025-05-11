from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Padelyzer API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para análisis de videos de pádel"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:8080",  # Frontend production
    ]
    
    # Video Processing
    MAX_VIDEO_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/quicktime"]
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hora por defecto
    SECRET_KEY: str = "supersecretkey123"
    ALGORITHM: str = "HS256"
    
    class Config:
        case_sensitive = True

settings = Settings() 