# app/routes/response_routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.response_factor_model import ResponseFactor
from app.models.factor_model import Factor
from app.models.possible_value_model import PossibleValue

# Crear Blueprint para las rutas de respuestas
response_bp = Blueprint('response', __name__)

# Endpoint para registrar una respuesta asociada a un factor y un valor posible
@response_bp.route('/api/responses', methods=['POST'])
def create_response():
    try:
        data = request.get_json()

        # Validar datos requeridos
        required_fields = ['encuesta_id', 'factor_id', 'valor_posible_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Convertir IDs a enteros
        encuesta_id = int(data['encuesta_id'])
        factor_id = int(data['factor_id'])
        valor_posible_id = int(data['valor_posible_id'])

        # Buscar el factor y el valor posible
        factor = Factor.query.get(factor_id)
        value = PossibleValue.query.get(valor_posible_id)

        if not factor:
            return jsonify({
                "error": True,
                "message": "Factor no encontrado"
            }), 404

        if not value:
            return jsonify({
                "error": True,
                "message": "Valor posible no encontrado"
            }), 404

        # Verificar que el valor pertenezca al factor
        if value.factor_id != factor.id:
            return jsonify({
                "error": True,
                "message": "El valor posible no pertenece al factor indicado"
            }), 400

        # Crear la respuesta dentro de una transacción
        with db.session.begin_nested():
            new_response = ResponseFactor(
                encuesta_id=encuesta_id,
                factor_id=factor.id,
                valor_posible_id=value.id,
                respuesta_texto=data.get('respuesta_texto', '')
            )
            db.session.add(new_response)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "data": new_response.to_dict(),
            "message": "Respuesta registrada exitosamente"
        }), 201

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al registrar la respuesta: {str(e)}"
        }), 500


# Endpoint para listar todas las respuestas
@response_bp.route('/api/responses', methods=['GET'])
def list_responses():
    try:
        responses = ResponseFactor.query.all()
        return jsonify({
            "success": True,
            "data": [response.to_dict() for response in responses],
            "message": "Respuestas obtenidas correctamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener las respuestas: {str(e)}"
        }), 500


# Endpoint para obtener una respuesta específica
@response_bp.route('/api/responses/<int:id>', methods=['GET'])
def get_response(id):
    try:
        response = ResponseFactor.query.get(id)
        if not response:
            return jsonify({
                "error": True,
                "message": "Respuesta no encontrada"
            }), 404

        return jsonify({
            "success": True,
            "data": response.to_dict(),
            "message": "Respuesta obtenida correctamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener la respuesta: {str(e)}"
        }), 500


# Endpoint para actualizar una respuesta
@response_bp.route('/api/responses/<int:id>', methods=['PUT'])
def update_response(id):
    try:
        data = request.get_json()
        response = ResponseFactor.query.get(id)

        if not response:
            return jsonify({
                "error": True,
                "message": "Respuesta no encontrada"
            }), 404

        # Actualizar campos de la respuesta
        if 'valor_posible_id' in data:
            value = PossibleValue.query.get(int(data['valor_posible_id']))
            if not value:
                return jsonify({
                    "error": True,
                    "message": "Valor posible no encontrado"
                }), 404
            response.valor_posible_id = value.id

        response.respuesta_texto = data.get('respuesta_texto', response.respuesta_texto)

        # Guardar cambios en la base de datos
        db.session.commit()

        return jsonify({
            "success": True,
            "data": response.to_dict(),
            "message": "Respuesta actualizada exitosamente"
        }), 200

    except ValueError as e:
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar la respuesta: {str(e)}"
        }), 500


# Endpoint para eliminar una respuesta
@response_bp.route('/api/responses/<int:id>', methods=['DELETE'])
def delete_response(id):
    try:
        response = ResponseFactor.query.get(id)

        if not response:
            return jsonify({
                "error": True,
                "message": "Respuesta no encontrada"
            }), 404

        # Eliminar la respuesta dentro de una transacción
        with db.session.begin_nested():
            db.session.delete(response)

        # Confirmar la transacción principal
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Respuesta eliminada exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar la respuesta: {str(e)}"
        }), 500