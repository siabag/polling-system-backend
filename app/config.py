# config.py
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:admin@localhost:3306/encuestas_cafe_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_default_secret_key")
    
    # Duración de los tokens JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)    # Access token: 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)  # Refresh token:  1 día