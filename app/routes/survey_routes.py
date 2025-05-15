# app/routes/survey_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models.survey_model import Survey
from app.models.user_model import User
from app.models.farm_model import Farm
from app.extensions import db

# Crear Blueprint para las rutas de encuestas
survey_bp = Blueprint('survey', __name__)

def get_survey_with_details(survey_id):

    survey = Survey.query.get(survey_id)
    if not survey:
        return None

    # Obtener datos relacionados
    farm = Farm.query.get(survey.finca_id)

    return {
        "id": survey.id,
        "fecha_aplicacion": survey.fecha_aplicacion.isoformat(),
        "observaciones": survey.observaciones,
        "completada": survey.completada,
        "usuario_id": survey.usuario_id,
        "finca_id": survey.finca_id,
        "finca": {
            "id": farm.id,
            "nombre": farm.nombre,
            "ubicacion": farm.ubicacion
        } if farm else None,
        "created_at": survey.created_at.isoformat(),
        "updated_at": survey.updated_at.isoformat() if survey.updated_at else None
    }

# Endpoint para crear una nueva encuesta
@survey_bp.route('/api/encuestas', methods=['POST'])
@jwt_required()
def create_encuesta():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validar datos requeridos
        required_fields = ['fecha_aplicacion', 'finca_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan campos requeridos"
            }), 400

        # Verificar que el usuario existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "error": True,
                "message": "Usuario no encontrado"
            }), 404

        # Verificar que la finca existe
        farm = Farm.query.get(data['finca_id'])
        if not farm:
            return jsonify({
                "error": True,
                "message": "Finca no encontrada"
            }), 404

        # Crear nueva encuesta dentro de una transacción
        with db.session.begin_nested():
            new_survey = Survey(
                fecha_aplicacion=data['fecha_aplicacion'],
                observaciones=data.get('observaciones', ''),
                completada=data.get('completada', False),
                usuario_id=user_id,
                finca_id=data['finca_id']
            )
            db.session.add(new_survey)

        # Confirmar la transacción principal
        db.session.commit()

        # Retornar detalles de la encuesta creada
        survey_data = get_survey_with_details(new_survey.id)
        return jsonify({
            "success": True,
            "data": survey_data,
            "message": "Encuesta creada exitosamente"
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear la encuesta: {str(e)}"
        }), 500


# Endpoint para obtener todas las encuestas de un usuario
@survey_bp.route('/api/encuestas', methods=['GET'])
@jwt_required()
def get_user_encuestas():
    try:
        user_id = get_jwt_identity()

        # Obtener encuestas del usuario
        surveys = Survey.query.filter_by(usuario_id=user_id).all()
        result = [get_survey_with_details(survey.id) for survey in surveys]

        return jsonify({
            "success": True,
            "data": result,
            "message": "Encuestas obtenidas exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener las encuestas: {str(e)}"
        }), 500


# Endpoint para obtener los detalles de una encuesta específica
@survey_bp.route('/api/encuestas/<int:survey_id>', methods=['GET'])
@jwt_required()
def get_encuesta(survey_id):
    try:
        user_id = get_jwt_identity()

        # Buscar la encuesta
        survey = Survey.query.get(survey_id)
        if not survey or survey.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Retornar detalles de la encuesta
        survey_data = get_survey_with_details(survey.id)
        return jsonify({
            "success": True,
            "data": survey_data,
            "message": "Encuesta obtenida exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener la encuesta: {str(e)}"
        }), 500


# Endpoint para actualizar una encuesta existente
@survey_bp.route('/api/encuestas/<int:survey_id>', methods=['PUT'])
@jwt_required()
def update_encuesta(survey_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Buscar la encuesta
        survey = Survey.query.get(survey_id)
        if not survey or survey.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Actualizar campos
        survey.fecha_aplicacion = data.get('fecha_aplicacion', survey.fecha_aplicacion)
        survey.observaciones = data.get('observaciones', survey.observaciones)
        survey.completada = data.get('completada', survey.completada)

        # Guardar cambios en la base de datos
        db.session.commit()

        # Retornar detalles actualizados de la encuesta
        survey_data = get_survey_with_details(survey.id)
        return jsonify({
            "success": True,
            "data": survey_data,
            "message": "Encuesta actualizada exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar la encuesta: {str(e)}"
        }), 500


# Endpoint para eliminar una encuesta
@survey_bp.route('/api/encuestas/<int:survey_id>', methods=['DELETE'])
@jwt_required()
def delete_encuesta(survey_id):
    try:
        user_id = get_jwt_identity()

        # Buscar la encuesta
        survey = Survey.query.get(survey_id)
        if not survey or survey.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Encuesta no encontrada o no autorizada"
            }), 404

        # Eliminar la encuesta dentro de una transacción
        with db.session.begin_nested():
            db.session.delete(survey)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Encuesta eliminada exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar la encuesta: {str(e)}"
        }), 500