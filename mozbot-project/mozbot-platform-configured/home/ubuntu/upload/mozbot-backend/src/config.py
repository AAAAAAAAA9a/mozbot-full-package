import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-strong-secret-key-here"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your-strong-jwt-secret-key-here"
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///instance/mozbot.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174") # Default to common frontend dev ports
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


