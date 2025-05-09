from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.response_factor_model import ResponseFactor
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue

# Crear Blueprint para las rutas de respuestas
response_bp = Blueprint('response', __name__)

# Endpoint para registrar una respuesta asociada a un factor y un valor posible
@response_bp.route('/api/responses', methods=['POST'])
def create_response():
    data = request.get_json()

    # Validar datos requeridos
    if not data or not data.get('encuesta_id') or not data.get('factor_id') or not data.get('valor_posible_id'):
        return jsonify({"msg": "Faltan datos requeridos"}), 400

    # Buscar el factor y el valor posible
    factor = Factor.query.get(data['factor_id'])
    value = PossibleValue.query.get(data['valor_posible_id'])

    if not factor:
        return jsonify({"msg": "Factor no encontrado"}), 404
    if not value:
        return jsonify({"msg": "Valor posible no encontrado"}), 404

    # Verificar que el valor pertenezca al factor
    if value.factor_id != factor.id:
        return jsonify({"msg": "El valor posible no pertenece al factor indicado"}), 400

    # Crear la respuesta
    new_response = ResponseFactor(
        encuesta_id=data['encuesta_id'],
        factor_id=factor.id,
        valor_posible_id=value.id,

    )

    # Guardar en la base de datos
    db.session.add(new_response)
    db.session.commit()

    return jsonify({
        "msg": "Respuesta registrada exitosamente",
        "response": new_response.to_dict()
    }), 201

# Endpoint para listar todas las respuestas
@response_bp.route('/api/responses', methods=['GET'])
def list_responses():
    responses = ResponseFactor.query.all()
    return jsonify([response.to_dict() for response in responses]), 200

# Endpoint para obtener una respuesta específica
@response_bp.route('/api/responses/<int:id>', methods=['GET'])
def get_response(id):
    response = ResponseFactor.query.get(id)
    if not response:
        return jsonify({"msg": "Respuesta no encontrada"}), 404

    return jsonify(response.to_dict()), 200

# Endpoint para actualizar una respuesta
@response_bp.route('/api/responses/<int:id>', methods=['PUT'])
def update_response(id):
    data = request.get_json()
    response = ResponseFactor.query.get(id)

    if not response:
        return jsonify({"msg": "Respuesta no encontrada"}), 404

    # Actualizar campos de la respuesta
    if data.get('valor_posible_id'):
        value = PossibleValue.query.get(data['valor_posible_id'])
        if not value:
            return jsonify({"msg": "Valor posible no encontrado"}), 404
        response.valor_posible_id = value.id

    response.respuesta_texto = data.get('respuesta_texto', response.respuesta_texto)

    # Guardar cambios en la base de datos
    db.session.commit()

    return jsonify({
        "msg": "Respuesta actualizada exitosamente",
        "response": response.to_dict()
    }), 200

# Endpoint para eliminar una respuesta
@response_bp.route('/api/responses/<int:id>', methods=['DELETE'])
def delete_response(id):
    response = ResponseFactor.query.get(id)

    if not response:
        return jsonify({"msg": "Respuesta no encontrada"}), 404

    # Eliminar la respuesta
    db.session.delete(response)
    db.session.commit()

    return jsonify({"msg": "Respuesta eliminada exitosamente"}), 200