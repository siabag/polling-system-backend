# config/config.py

"""
Configuración central del backend
Clasificador de Hojas de Café con YOLO + SAM + ResNet
"""

import os

class Config:
    """Configuración base"""
    
    # Flask
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Rutas
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
    
    # Modelos
    MODELS = {
        'YOLO': {
            'weights': os.path.join(MODELS_DIR, 'yolo_best.pt'),
            'imgsz': 960,
            'conf': 0.40,
            'device': 'cpu',  # Cambia a 'cuda' si tienes GPU
        },
        'SAM': {
            'checkpoint': os.path.join(MODELS_DIR, 'sam_vit_b_01ec64.pth'),
            'model': 'vit_b',  # vit_b es 3x más rápido que vit_h
            'points_per_side': 8,  # De 16 a 8 = más rápido, precisión similar
            'pred_iou_thresh': 0.90,
            'stability_score_thresh': 0.95,
            'min_mask_region_area': 100,
            'device': 'cpu',
        },
        'RESNET': {
            'weights': os.path.join(MODELS_DIR, 'resnet18_best.pt'),
            'device': 'cpu',
        }
    }
    
    # Configuración SAM
    SAM_MODE = 'off'  # 'off', 'classify', o 'save'
    
    # Estrategias de optimización
    OPTIMIZATION = {
        'use_parallel': True,  # Procesar detecciones en paralelo
        'max_workers': 4,  # Número de workers para paralelización
        'yolo_confidence_threshold': 0.85,  # Si YOLO > 0.85, no usar SAM
        'use_sam_selective': True,  # Solo usar SAM en detecciones de baja confianza
    }
    
    # Límites
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    
    # API
    API_TIMEOUT = 300  # 5 minutos

config = Config()
