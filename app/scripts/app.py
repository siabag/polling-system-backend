# app.py

"""
Backend Flask para Clasificador de Hojas de Café
Endpoint: POST /api/v1/classification/analyze
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import tempfile
from config.config import config
from scripts.analyze_service import create_analysis_service

app = Flask(__name__)
CORS(app)

# Crear carpeta de uploads
os.makedirs(config.UPLOADS_DIR, exist_ok=True)

# Inicializar servicio de análisis
print("[INIT] Cargando servicio de análisis...")
try:
    analysis_service = create_analysis_service(config.MODELS)
    print("[INIT] Servicio cargado exitosamente")
except Exception as e:
    print(f"[ERROR] No se pudo cargar el servicio: {e}")
    analysis_service = None


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint para verificar que el servidor está corriendo"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend está funcionando',
        'service_ready': analysis_service is not None
    })


@app.route('/api/v1/classification/analyze', methods=['POST'])
def analyze():
    """
    Endpoint principal para clasificación de imágenes
    
    Recibe:
        - image: archivo de imagen (multipart/form-data)
    
    Devuelve:
        - success: bool
        - message: string
        - data: objeto con resultados
    """
    
    try:
        # Verificar servicio
        if analysis_service is None:
            return jsonify({
                'success': False,
                'error': 'Servicio de análisis no disponible'
            }), 500
        
        # Verificar que hay imagen
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Por favor proporciona una imagen'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename',
                'message': 'El archivo está vacío'
            }), 400
        
        # Validar extensión
        allowed_ext = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in allowed_ext:
            return jsonify({
                'success': False,
                'error': 'Invalid file format',
                'message': f'Formato no soportado. Usa: {", ".join(allowed_ext)}'
            }), 400
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            image_file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Analizar imagen
            print(f"[ANALYZE] Procesando: {image_file.filename}")
            results = analysis_service.analyze_image(temp_path)
            
            # Respuesta exitosa
            response = {
                'success': True,
                'message': 'Clasificación completada exitosamente',
                'data': {
                    'totalLeavesDetected': results['total_leaves'],
                    'healthyLeaves': results['healthy_leaves'],
                    'affectedLeaves': results['affected_leaves'],
                    'processedImage': results['processed_image_base64'],
                    'confidence': results['confidence'],
                    'timestamp': results['timestamp']
                }
            }
            
            print(f"[ANALYZE] ✓ Éxito: {results['total_leaves']} hojas detectadas")
            return jsonify(response), 200
        
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al procesar la imagen'
        }), 500


@app.route('/api/v1/status', methods=['GET'])
def status():
    """Endpoint para ver estado del servicio y modelos"""
    
    return jsonify({
        'status': 'running',
        'service_ready': analysis_service is not None,
        'device': str(analysis_service.device) if analysis_service else 'N/A',
        'models': {
            'yolo': os.path.exists(config.MODELS['YOLO']['weights']),
            'classifier': os.path.exists(config.MODELS['RESNET']['weights']),
            'sam': os.path.exists(config.MODELS['SAM']['checkpoint']) if 'checkpoint' in config.MODELS.get('SAM', {}) else False,
        },
        'config': {
            'yolo_imgsz': config.MODELS['YOLO']['imgsz'],
            'yolo_conf': config.MODELS['YOLO']['conf'],
            'device': config.MODELS['YOLO']['device'],
        }
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Clasificador de Hojas de Café - Backend Flask")
    print("="*60)
    print(f"Escuchando en http://localhost:5000")
    print(f"Endpoint: POST /api/v1/classification/analyze")
    print(f"Health check: GET /api/health")
    print(f"Status: GET /api/v1/status")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')