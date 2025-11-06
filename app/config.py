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

    # NUEVA CONFIGURACIÓN PARA EL SERVICIO DE ANÁLISIS (AGREGAR AL FINAL)
    # Rutas base para modelos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
    
    # Configuración de modelos (para el servicio de análisis)
    MODELS = {
        'YOLO': {
            'weights': os.path.join(MODELS_DIR, 'yolo_best.pt'),
            'imgsz': 320,                 # Tamaño óptimo: 640px
            'imgsz_range': [320, 1280],      # Rango permitido: 320-1280px
            'conf': 0.15,                    # Confianza inicial
            'conf_range': [0.10, 0.30],      # Rango de confianza: 15%-50%
            'iou': 0.35,                     # IOU estándar
            'device': 'cpu',
        },
        'SAM': {
            'checkpoint': os.path.join(MODELS_DIR, 'sam_vit_b_01ec64.pth'),
            'model': 'vit_b',
            'points_per_side': 8,
            'pred_iou_thresh': 0.90,
            'stability_score_thresh': 0.95,
            'min_mask_region_area': 100,
            'device': 'cpu',
            'mode': 'classify'
        },
        'RESNET': {
            'weights': os.path.join(MODELS_DIR, 'resnet18_best.pt'),
            'device': 'cpu',
        }
    }
    
    SAM_MODE = 'classify'  # 'off', 'classify', 'save'
    
    # Límites de archivo para análisis
    MAX_FILE_SIZE = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

config = Config()