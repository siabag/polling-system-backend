# check_models.py
import os
from app.config import config

def check_models():
    print("🔍 Verificando archivos de modelos...")
    
    # Verificar YOLO
    yolo_path = config.MODELS['YOLO']['weights']
    print(f"YOLO: {yolo_path} - Existe: {os.path.exists(yolo_path)}")
    
    # Verificar ResNet
    resnet_path = config.MODELS['RESNET']['weights']
    print(f"ResNet: {resnet_path} - Existe: {os.path.exists(resnet_path)}")
    
    # Verificar SAM
    sam_path = config.MODELS['SAM']['checkpoint']
    print(f"SAM: {sam_path} - Existe: {os.path.exists(sam_path)}")
    
    # Verificar directorio de modelos
    models_dir = config.MODELS_DIR
    print(f"📁 Directorio de modelos: {models_dir}")
    if os.path.exists(models_dir):
        print("📄 Archivos en el directorio:")
        for file in os.listdir(models_dir):
            print(f"  - {file}")

if __name__ == "__main__":
    check_models()