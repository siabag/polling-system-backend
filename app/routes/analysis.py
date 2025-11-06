# app/routes/analysis.py
from flask import Blueprint, request, jsonify
import os
import tempfile
import traceback

# Blueprint para las rutas de análisis
analysis_bp = Blueprint('analysis', __name__)

print("=" * 60)
print("🔧 INICIALIZANDO MÓDULO DE ANÁLISIS")
print("=" * 60)

# Intentar importar el servicio de análisis
try:
    from app.scripts.analyze_service import create_analysis_service
    ANALYSIS_AVAILABLE = True
    print("✅ Módulo analyze_service importado correctamente")
except ImportError as e:
    print(f"❌ Error importando analyze_service: {e}")
    traceback.print_exc()
    ANALYSIS_AVAILABLE = False
    create_analysis_service = None

# Inicializar servicio (singleton)
analysis_service = None

def get_analysis_service():
    global analysis_service
    print(f"🔄 get_analysis_service() llamado - analysis_service es None: {analysis_service is None}")
    
    if analysis_service is None and ANALYSIS_AVAILABLE:
        try:
            print("🚀 Intentando inicializar el servicio de análisis...")
            
            # Importar la configuración
            from app.config import config
            print(f"📋 Configuración cargada:")
            print(f"   - YOLO: {config.MODELS['YOLO']['weights']}")
            print(f"   - ResNet: {config.MODELS['RESNET']['weights']}")
            print(f"   - SAM: {config.MODELS['SAM']['checkpoint']}")
            
            # Verificar que los archivos existan
            yolo_exists = os.path.exists(config.MODELS['YOLO']['weights'])
            resnet_exists = os.path.exists(config.MODELS['RESNET']['weights'])
            sam_exists = os.path.exists(config.MODELS['SAM']['checkpoint'])
            
            print(f"📁 Verificación de archivos:")
            print(f"   - YOLO existe: {yolo_exists}")
            print(f"   - ResNet existe: {resnet_exists}")
            print(f"   - SAM existe: {sam_exists}")
            
            if not all([yolo_exists, resnet_exists]):
                print("❌ Faltan archivos de modelos esenciales")
                return None
            
            print("🎯 Creando servicio de análisis...")
            analysis_service = create_analysis_service(config.MODELS)
            print("✅ Servicio de análisis creado exitosamente")
            
        except Exception as e:
            print(f"💥 ERROR CRÍTICO inicializando el servicio: {e}")
            print("🔍 Traceback completo:")
            traceback.print_exc()
            analysis_service = None
    
    return analysis_service

@analysis_bp.route('/api/v1/classification/health', methods=['GET'])
def health():
    """Health check del servicio de análisis"""
    print("\n🏥 HEALTH CHECK solicitado")
    service = get_analysis_service()
    
    response = {
        'status': 'ok' if service else 'error',
        'service_ready': service is not None,
        'analysis_available': ANALYSIS_AVAILABLE,
        'message': 'Servicio listo' if service else 'Servicio no disponible'
    }
    
    print(f"📊 Health response: {response}")
    return jsonify(response)

@analysis_bp.route('/api/v1/classification/analyze', methods=['POST'])
def analyze():
    """
    Endpoint principal para clasificación de imágenes
    """
    print("\n📨 SOLICITUD DE ANÁLISIS RECIBIDA")
    
    # Verificar si el análisis está disponible
    if not ANALYSIS_AVAILABLE:
        print("❌ ANALYSIS_AVAILABLE = False")
        return jsonify({
            'success': False,
            'error': 'Analysis service not available',
            'message': 'El servicio de análisis no está disponible'
        }), 503
    
    try:
        # Verificar servicio
        service = get_analysis_service()
        print(f"🔍 Servicio obtenido: {'✅ No es None' if service else '❌ Es None'}")
        
        if service is None:
            print("❌ El servicio es None - retornando 503")
            return jsonify({
                'success': False,
                'error': 'Servicio de análisis no disponible',
                'message': 'El servicio no pudo inicializarse'
            }), 503

        # Verificar imagen
        if 'image' not in request.files:
            print("❌ No se envió imagen en request.files")
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Por favor proporciona una imagen'
            }), 400

        image_file = request.files['image']
        print(f"📸 Archivo recibido: {image_file.filename}")
        
        if image_file.filename == '':
            print("❌ Nombre de archivo vacío")
            return jsonify({
                'success': False,
                'error': 'Empty filename',
                'message': 'El archivo está vacío'
            }), 400

        # Validar extensión
        allowed_ext = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        print(f"📄 Extensión del archivo: {file_ext}")
        
        if file_ext not in allowed_ext:
            print(f"❌ Extensión no permitida: {file_ext}")
            return jsonify({
                'success': False,
                'error': 'Invalid file format',
                'message': f'Formato no soportado. Usa: {", ".join(allowed_ext)}'
            }), 400

        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            image_file.save(tmp.name)
            temp_path = tmp.name

        print(f"💾 Imagen guardada en: {temp_path}")

        try:
            # Analizar imagen
            print("🔄 Llamando a service.analyze_image()...")
            results = service.analyze_image(temp_path)
            print(f"✅ Análisis completado: {results['total_leaves']} hojas detectadas")
            
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
            
            return jsonify(response), 200

        except Exception as analyze_error:
            print(f"💥 Error en analyze_image: {analyze_error}")
            traceback.print_exc()
            raise analyze_error

        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"🧹 Archivo temporal eliminado: {temp_path}")

    except Exception as e:
        print(f"💥 ERROR GENERAL: {str(e)}")
        print("🔍 Traceback completo:")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error al procesar la imagen'
        }), 500

@analysis_bp.route('/api/v1/classification/status', methods=['GET'])
def status():
    """Estado del servicio y modelos"""
    print("\n📊 STATUS solicitado")
    service = get_analysis_service()
    
    status_info = {
        'status': 'running',
        'service_ready': service is not None,
        'analysis_available': ANALYSIS_AVAILABLE,
        'models_loaded': False
    }
    
    if service:
        from config import config
        status_info.update({
            'device': str(service.device),
            'models_loaded': True,
            'models': {
                'yolo': os.path.exists(config.MODELS['YOLO']['weights']),
                'classifier': os.path.exists(config.MODELS['RESNET']['weights']),
                'sam': os.path.exists(config.MODELS['SAM']['checkpoint']),
            }
        })
    
    print(f"📈 Status response: {status_info}")
    return jsonify(status_info)

print("=" * 60)
print("✅ MÓDULO DE ANÁLISIS CARGADO")
print("=" * 60)