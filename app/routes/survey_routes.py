from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.survey_model import Survey
from app.models.user_model import User
from app.extensions import db

# Crear Blueprint para las rutas de encuestas
survey_bp = Blueprint('survey', __name__)

# Endpoint para crear una nueva encuesta
@survey_bp.route('/surveys', methods=['POST'])
@jwt_required()  # Proteger esta ruta con JWT
def create_survey():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validar datos de entrada
    required_fields = ['fecha_aplicacion', 'observaciones', 'finca_id']
    if not all(field in data for field in required_fields):
        return jsonify({"msg": "Faltan campos requeridos"}), 400

    # Verificar que el usuario existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # Crear nueva encuesta
    new_survey = Survey(
        fecha_aplicacion=data['fecha_aplicacion'],
        observaciones=data.get('observaciones'),
        completada=data.get('completada', False),
        usuario_id=user_id,
        finca_id=data['finca_id']
    )

    # Guardar en la base de datos
    db.session.add(new_survey)
    db.session.commit()

    return jsonify({"msg": "Encuesta creada exitosamente", "survey_id": new_survey.id}), 201

# Endpoint para obtener todas las encuestas de un usuario
@survey_bp.route('/surveys', methods=['GET'])
@jwt_required()
def get_user_surveys():
    user_id = get_jwt_identity()

    # Obtener encuestas del usuario
    surveys = Survey.query.filter_by(usuario_id=user_id).all()
    result = [
        {
            "id": survey.id,
            "fecha_aplicacion": survey.fecha_aplicacion,
            "observaciones": survey.observaciones,
            "completada": survey.completada,
            "finca_id": survey.finca_id
        }
        for survey in surveys
    ]

    return jsonify(result), 200

# Endpoint para actualizar una encuesta existente
@survey_bp.route('/surveys/<int:survey_id>', methods=['PUT'])
@jwt_required()
def update_survey(survey_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    # Buscar la encuesta
    survey = Survey.query.get(survey_id)
    if not survey or survey.usuario_id != user_id:
        return jsonify({"msg": "Encuesta no encontrada o no autorizada"}), 404

    # Actualizar campos
    survey.fecha_aplicacion = data.get('fecha_aplicacion', survey.fecha_aplicacion)
    survey.observaciones = data.get('observaciones', survey.observaciones)
    survey.completada = data.get('completada', survey.completada)

    # Guardar cambios
    db.session.commit()

    return jsonify({"msg": "Encuesta actualizada exitosamente"}), 200

# Endpoint para eliminar una encuesta
@survey_bp.route('/surveys/<int:survey_id>', methods=['DELETE'])
@jwt_required()
def delete_survey(survey_id):
    user_id = get_jwt_identity()

    # Buscar la encuesta
    survey = Survey.query.get(survey_id)
    if not survey or survey.usuario_id != user_id:
        return jsonify({"msg": "Encuesta no encontrada o no autorizada"}), 404

    # Eliminar la encuesta
    db.session.delete(survey)
    db.session.commit()

    return jsonify({"msg": "Encuesta eliminada exitosamente"}), 200