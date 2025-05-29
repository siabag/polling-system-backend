# app/routes/survey_type_routes.py

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from app.models.survey_type_model import SurveyType
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue
from app.extensions import db

# Crear Blueprint para las rutas de tipos de encuesta
survey_type_bp = Blueprint('survey_type', __name__)

# Endpoint para obtener los factores de un tipo de encuesta específico
@survey_type_bp.route('/api/tipos-encuesta/<int:id>/factores', methods=['GET'])
def get_factors_by_survey_type(id):
    try:
        # Buscar el tipo de encuesta por ID
        survey_type = SurveyType.query.get(id)
        if not survey_type:
            return jsonify({
                "error": True,
                "message": "Tipo de encuesta no encontrado"
            }), 404

        # Obtener los factores asociados al tipo de encuesta
        factors = survey_type.factores
        if not factors:
            return jsonify({
                "success": True,
                "data": [],
                "message": "No hay factores asociados a este tipo de encuesta"
            }), 200

        # Formatear los datos de los factores y sus valores posibles
        result = []
        for factor in factors:
            factor_data = {
                "id": factor.id,
                "nombre": factor.nombre,
                "descripcion": factor.descripcion,
                "categoria": factor.categoria,
                "activo": factor.activo,
                "tipo_encuesta_id": factor.tipo_encuesta_id,
                "valores_posibles": [
                    {
                        "id": value.id,
                        "factor_id": value.factor_id,
                        "valor": value.valor,
                        "codigo": value.codigo,
                        "descripcion": value.descripcion,
                        "activo": value.activo
                    }
                    for value in factor.valores_posibles
                ]
            }
            result.append(factor_data)

        return jsonify({
            "success": True,
            "data": result,
            "message": "Factores obtenidos exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los factores: {str(e)}"
        }), 500

# Endpoint para obtener un tipo de encuesta por ID
@survey_type_bp.route('/api/tipos-encuesta/<int:type_id>', methods=['GET'])
def get_survey_type_by_id(type_id):
    try:
        # Buscar el tipo de encuesta por ID
        survey_type = SurveyType.query.get(type_id)
        if not survey_type:
            return jsonify({
                "error": True,
                "message": "Tipo de encuesta no encontrado"
            }), 404

        # Formatear los datos del tipo de encuesta
        survey_type_data = {
            "id": survey_type.id,
            "nombre": survey_type.nombre,
            "descripcion": survey_type.descripcion,
            "activo": survey_type.activo,
            "created_at": survey_type.created_at.isoformat(),
            "updated_at": survey_type.updated_at.isoformat() if survey_type.updated_at else None
        }

        return jsonify({
            "success": True,
            "data": survey_type_data,
            "message": "Tipo de encuesta obtenido exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener el tipo de encuesta: {str(e)}"
        }), 500

# Endpoint para listar todos los tipos de encuesta
@survey_type_bp.route('/api/tipos-encuesta', methods=['GET'])
def list_survey_types():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)

        # Consultar todos los tipos de encuesta con paginación
        query = SurveyType.query.filter_by(activo=True)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Formatear los datos de los tipos de encuesta
        survey_types_data = []
        for survey_type in pagination.items:
            survey_types_data.append({
                "id": survey_type.id,
                "nombre": survey_type.nombre,
                "descripcion": survey_type.descripcion,
                "activo": survey_type.activo,
                "created_at": survey_type.created_at.isoformat(),
                "updated_at": survey_type.updated_at.isoformat() if survey_type.updated_at else None
            })

        return jsonify({
            "success": True,
            "data": survey_types_data,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages,
            "message": "Tipos de encuesta obtenidos exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al listar los tipos de encuesta: {str(e)}"
        }), 500