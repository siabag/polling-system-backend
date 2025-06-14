# app/routes/survey_reports.py

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import csv
import io
from app.extensions import db
from app.models.survey_model import Survey
from app.models.farm_model import Farm
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue
from app.models.response_factor_model import ResponseFactor
from app.models.survey_type_model import SurveyType

# Crear Blueprint para los reportes de encuestas
reports_bp = Blueprint('reports', __name__)

def generate_csv_content(encuestas_data):
    """
    Genera el contenido CSV a partir de los datos de encuestas
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Encabezados del CSV
    headers = [
        'ID Encuesta',
        'Fecha Aplicación',
        'Tipo Encuesta',
        'Finca',
        'Ubicación Finca',
        'Propietario',
        'Completada',
        'Observaciones',
        'Factor',
        'Categoría Factor',
        'Valor Seleccionado',
        'Código Valor',
        'Descripción Valor',
        'Comentario Respuesta',
        'Fecha Creación',
        'Última Actualización'
    ]
    writer.writerow(headers)
    
    # Escribir datos
    for encuesta in encuestas_data:
        base_row = [
            encuesta['id'],
            encuesta['fecha_aplicacion'],
            encuesta['tipo_encuesta']['nombre'] if encuesta['tipo_encuesta'] else '',
            encuesta['finca']['nombre'] if encuesta['finca'] else '',
            encuesta['finca']['ubicacion'] if encuesta['finca'] else '',
            encuesta['finca']['propietario'] if encuesta['finca'] else '',
            'Sí' if encuesta['completada'] else 'No',
            encuesta['observaciones'] or '',
        ]
        
        # Si no hay respuestas, escribir una fila con los datos básicos
        if not encuesta['respuestas']:
            row = base_row + ['', '', '', '', '', '', '', '']
            writer.writerow(row)
        else:
            # Una fila por cada respuesta
            for respuesta in encuesta['respuestas']:
                row = base_row + [
                    respuesta['factor']['nombre'] if respuesta['factor'] else '',
                    respuesta['factor']['categoria'] if respuesta['factor'] else '',
                    respuesta['valor_posible']['valor'] if respuesta['valor_posible'] else '',
                    respuesta['valor_posible']['codigo'] if respuesta['valor_posible'] else '',
                    respuesta['valor_posible']['descripcion'] if respuesta['valor_posible'] else '',
                    respuesta['respuesta_texto'] or '',
                    encuesta['created_at'],
                    encuesta['updated_at'] or ''
                ]
                writer.writerow(row)
    
    content = output.getvalue()
    output.close()
    return content

def get_encuestas_for_report(user_id, filters):
    """
    Obtiene las encuestas con todos los datos necesarios para el reporte
    """
    query = Survey.query.filter_by(usuario_id=user_id)
    
    # Aplicar filtros
    if filters.get('fecha_inicio'):
        fecha_inicio = datetime.strptime(filters['fecha_inicio'], '%Y-%m-%d').date()
        query = query.filter(Survey.fecha_aplicacion >= fecha_inicio)
    
    if filters.get('fecha_fin'):
        fecha_fin = datetime.strptime(filters['fecha_fin'], '%Y-%m-%d').date()
        query = query.filter(Survey.fecha_aplicacion <= fecha_fin)
    
    if filters.get('tipo_encuesta_id'):
        query = query.filter_by(tipo_encuesta_id=filters['tipo_encuesta_id'])
    
    if filters.get('finca_id'):
        query = query.filter_by(finca_id=filters['finca_id'])
    
    if filters.get('completada') is not None:
        query = query.filter_by(completada=filters['completada'])
    
    # Ordenar por fecha de aplicación (más recientes primero)
    query = query.order_by(Survey.fecha_aplicacion.desc())
    
    encuestas = query.all()
    
    # Convertir a formato dict con todos los datos necesarios
    result = []
    for encuesta in encuestas:
        encuesta_data = {
            "id": encuesta.id,
            "fecha_aplicacion": encuesta.fecha_aplicacion.isoformat(),
            "tipo_encuesta_id": encuesta.tipo_encuesta_id,
            "usuario_id": encuesta.usuario_id,
            "finca_id": encuesta.finca_id,
            "observaciones": encuesta.observaciones,
            "completada": encuesta.completada,
            "created_at": encuesta.created_at.isoformat(),
            "updated_at": encuesta.updated_at.isoformat() if encuesta.updated_at else None,
            "tipo_encuesta": {
                "id": encuesta.tipo_encuesta.id,
                "nombre": encuesta.tipo_encuesta.nombre,
                "descripcion": encuesta.tipo_encuesta.descripcion,
                "activo": encuesta.tipo_encuesta.activo,
                "created_at": encuesta.tipo_encuesta.created_at.isoformat(),
                "updated_at": encuesta.tipo_encuesta.updated_at.isoformat() if encuesta.tipo_encuesta.updated_at else None
            } if encuesta.tipo_encuesta else None,
            "finca": {
                "id": encuesta.finca.id,
                "nombre": encuesta.finca.nombre,
                "ubicacion": encuesta.finca.ubicacion,
                "latitud": str(encuesta.finca.latitud) if encuesta.finca.latitud else None,
                "longitud": str(encuesta.finca.longitud) if encuesta.finca.longitud else None,
                "propietario": encuesta.finca.propietario,
                "usuario_id": encuesta.finca.usuario_id,
                "created_at": encuesta.finca.created_at.isoformat(),
                "updated_at": encuesta.finca.updated_at.isoformat() if encuesta.finca.updated_at else None
            } if encuesta.finca else None,
            "respuestas": [
                {
                    "id": respuesta.id,
                    "encuesta_id": respuesta.encuesta_id,
                    "factor_id": respuesta.factor_id,
                    "valor_posible_id": respuesta.valor_posible_id,
                    "respuesta_texto": respuesta.respuesta_texto,
                    "created_at": respuesta.created_at.isoformat(),
                    "updated_at": respuesta.updated_at.isoformat() if respuesta.updated_at else None,
                    "factor": {
                        "id": respuesta.factor.id,
                        "nombre": respuesta.factor.nombre,
                        "descripcion": respuesta.factor.descripcion,
                        "categoria": respuesta.factor.categoria,
                        "activo": respuesta.factor.activo,
                        "tipo_encuesta_id": respuesta.factor.tipo_encuesta_id,
                        "created_at": respuesta.factor.created_at.isoformat(),
                        "updated_at": respuesta.factor.updated_at.isoformat() if respuesta.factor.updated_at else None
                    },
                    "valor_posible": {
                        "id": respuesta.valor_posible.id,
                        "factor_id": respuesta.valor_posible.factor_id,
                        "valor": respuesta.valor_posible.valor,
                        "codigo": respuesta.valor_posible.codigo,
                        "descripcion": respuesta.valor_posible.descripcion,
                        "activo": respuesta.valor_posible.activo,
                        "created_at": respuesta.valor_posible.created_at.isoformat(),
                        "updated_at": respuesta.valor_posible.updated_at.isoformat() if respuesta.valor_posible.updated_at else None
                    }
                }
                for respuesta in encuesta.respuestas
            ]
        }
        result.append(encuesta_data)
    
    return result

# Endpoint para generar reporte CSV de encuestas
@reports_bp.route('/api/reportes/encuestas/csv', methods=['GET'])
@jwt_required()
def generate_encuestas_csv_report():
    try:
        user_id = get_jwt_identity()
        
        # Obtener parámetros de filtro
        filters = {
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin'),
            'tipo_encuesta_id': request.args.get('tipo_encuesta_id', type=int),
            'finca_id': request.args.get('finca_id', type=int),
            'completada': request.args.get('completada', type=bool) if request.args.get('completada') else None,
        }
        
        # Remover filtros vacíos
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Obtener datos de encuestas
        encuestas_data = get_encuestas_for_report(user_id, filters)
        
        if not encuestas_data:
            return jsonify({
                "error": True,
                "message": "No se encontraron encuestas con los filtros aplicados"
            }), 404
        
        # Generar contenido CSV
        csv_content = generate_csv_content(encuestas_data)
        
        # Crear respuesta con el archivo CSV
        output = make_response(csv_content)
        
        # Generar nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_encuestas_{timestamp}.csv"
        
        # Configurar headers para descarga
        output.headers["Content-Disposition"] = f"attachment; filename={filename}"
        output.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return output

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Formato de fecha inválido: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al generar el reporte: {str(e)}"
        }), 500

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error inesperado: {str(e)}"
        }), 500

# Endpoint para obtener vista previa del reporte (JSON)
@reports_bp.route('/api/reportes/encuestas/preview', methods=['GET'])
@jwt_required()
def preview_encuestas_report():
    try:
        user_id = get_jwt_identity()
        
        # Obtener parámetros de filtro
        filters = {
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin'),
            'tipo_encuesta_id': request.args.get('tipo_encuesta_id', type=int),
            'finca_id': request.args.get('finca_id', type=int),
            'completada': request.args.get('completada', type=bool) if request.args.get('completada') else None,
        }
        
        # Remover filtros vacíos
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Obtener parámetros de paginación para la vista previa
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        
        # Obtener datos de encuestas (solo para vista previa)
        encuestas_data = get_encuestas_for_report(user_id, filters)
        
        # Aplicar paginación para la vista previa
        total = len(encuestas_data)
        start = (page - 1) * per_page
        end = start + per_page
        encuestas_preview = encuestas_data[start:end]
        
        return jsonify({
            "success": True,
            "data": encuestas_preview,
            "total": total,
            "page": page,
            "totalPages": (total + per_page - 1) // per_page,
            "filters_applied": filters,
            "message": f"Vista previa del reporte ({total} registros encontrados)"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Formato de fecha inválido: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al generar la vista previa: {str(e)}"
        }), 500

# Endpoint para obtener resumen estadístico del reporte
@reports_bp.route('/api/reportes/encuestas/estadisticas', methods=['GET'])
@jwt_required()
def get_encuestas_statistics():
    try:
        user_id = get_jwt_identity()
        
        # Obtener parámetros de filtro
        filters = {
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin'),
            'tipo_encuesta_id': request.args.get('tipo_encuesta_id', type=int),
            'finca_id': request.args.get('finca_id', type=int),
            'completada': request.args.get('completada', type=bool) if request.args.get('completada') else None,
        }
        
        # Remover filtros vacíos
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Obtener datos de encuestas
        encuestas_data = get_encuestas_for_report(user_id, filters)
        
        # Calcular estadísticas
        total_encuestas = len(encuestas_data)
        completadas = sum(1 for e in encuestas_data if e['completada'])
        pendientes = total_encuestas - completadas
        
        # Estadísticas por tipo de encuesta
        tipos_stats = {}
        for encuesta in encuestas_data:
            tipo_nombre = encuesta['tipo_encuesta']['nombre'] if encuesta['tipo_encuesta'] else 'Sin tipo'
            if tipo_nombre not in tipos_stats:
                tipos_stats[tipo_nombre] = {'total': 0, 'completadas': 0}
            tipos_stats[tipo_nombre]['total'] += 1
            if encuesta['completada']:
                tipos_stats[tipo_nombre]['completadas'] += 1
        
        # Estadísticas por finca
        fincas_stats = {}
        for encuesta in encuestas_data:
            finca_nombre = encuesta['finca']['nombre'] if encuesta['finca'] else 'Sin finca'
            if finca_nombre not in fincas_stats:
                fincas_stats[finca_nombre] = {'total': 0, 'completadas': 0}
            fincas_stats[finca_nombre]['total'] += 1
            if encuesta['completada']:
                fincas_stats[finca_nombre]['completadas'] += 1
        
        return jsonify({
            "success": True,
            "data": {
                "resumen_general": {
                    "total_encuestas": total_encuestas,
                    "completadas": completadas,
                    "pendientes": pendientes,
                    "porcentaje_completadas": round((completadas / total_encuestas * 100), 2) if total_encuestas > 0 else 0
                },
                "por_tipo_encuesta": tipos_stats,
                "por_finca": fincas_stats,
                "filtros_aplicados": filters
            },
            "message": "Estadísticas generadas exitosamente"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Formato de fecha inválido: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al generar las estadísticas: {str(e)}"
        }), 500