# app/routes/survey_type_routes.py

from flask import Blueprint, jsonify
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