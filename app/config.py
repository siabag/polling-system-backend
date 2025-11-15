# config.py
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

class Config:
    # CONFIGURACIÓN EXISTENTE (NO CAMBIAR)
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/encuestas_cafe_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_default_secret_key")
    
    # Duración de los tokens JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)    # Access token: 7 días
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token: 30 días