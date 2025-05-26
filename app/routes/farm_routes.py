# app/routes/farm_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.farm_model import Farm
from app.models.user_model import User

# Crear Blueprint para las rutas de fincas
farm_bp = Blueprint('farm', __name__)

# Endpoint para crear una nueva finca
@farm_bp.route('/api/fincas', methods=['POST'])
@jwt_required()
def create_farm():
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Validar datos recibidos del frontend
        data = request.get_json()
        required_fields = ['nombre', 'ubicacion', 'propietario']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Convertir latitud y longitud a números si están presentes
        latitud = float(data['latitud']) if 'latitud' in data and data['latitud'] is not None else None
        longitud = float(data['longitud']) if 'longitud' in data and data['longitud'] is not None else None

        # Verificar que el usuario exista
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "error": True,
                "message": "Usuario no encontrado"
            }), 404

        # Crear la nueva finca dentro de una transacción
        with db.session.begin_nested():
            new_farm = Farm(
                nombre=data['nombre'],
                ubicacion=data['ubicacion'],
                latitud=latitud,
                longitud=longitud,
                propietario=data['propietario'],
                usuario_id=user_id
            )
            db.session.add(new_farm)

        # Confirmar la transacción
        db.session.commit()

        # Retornar la respuesta JSON
        return jsonify({
            "success": True,
            "data": new_farm.to_dict(),
            "message": "Finca creada exitosamente"
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear la finca: {str(e)}"
        }), 500


# Endpoint para actualizar una finca existente
@farm_bp.route('/api/fincas/<int:farm_id>', methods=['PUT'])
@jwt_required()
def update_farm(farm_id):
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Buscar la finca
        farm = Farm.query.get(farm_id)
        if not farm or farm.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Finca no encontrada o no autorizada"
            }), 404

        # Validar datos recibidos del frontend
        data = request.get_json()

        # Actualizar campos
        farm.nombre = data.get('nombre', farm.nombre)
        farm.ubicacion = data.get('ubicacion', farm.ubicacion)
        farm.latitud = float(data['latitud']) if 'latitud' in data and data['latitud'] is not None else farm.latitud
        farm.longitud = float(data['longitud']) if 'longitud' in data and data['longitud'] is not None else farm.longitud
        farm.propietario = data.get('propietario', farm.propietario)

        # Confirmar cambios en la base de datos
        db.session.commit()

        # Retornar la respuesta JSON
        return jsonify({
            "success": True,
            "data": farm.to_dict(),
            "message": "Finca actualizada exitosamente"
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Datos inválidos: {str(e)}"
        }), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar la finca: {str(e)}"
        }), 500


# Endpoint para obtener una finca por ID
@farm_bp.route('/api/fincas/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_farm(farm_id):
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Buscar la finca
        farm = Farm.query.get(farm_id)
        if not farm or farm.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Finca no encontrada o no autorizada"
            }), 404

        # Retornar la respuesta JSON
        return jsonify({
            "success": True,
            "data": farm.to_dict(),
            "message": "Finca obtenida exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener la finca: {str(e)}"
        }), 500


# Endpoint para eliminar una finca
@farm_bp.route('/api/fincas/<int:farm_id>', methods=['DELETE'])
@jwt_required()
def delete_farm(farm_id):
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Buscar la finca
        farm = Farm.query.get(farm_id)
        if not farm or farm.usuario_id != user_id:
            return jsonify({
                "error": True,
                "message": "Finca no encontrada o no autorizada"
            }), 404

        # Eliminar la finca dentro de una transacción
        with db.session.begin_nested():
            db.session.delete(farm)

        # Confirmar la transacción
        db.session.commit()

        # Retornar la respuesta JSON
        return jsonify({
            "success": True,
            "message": "Finca eliminada exitosamente"
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar la finca: {str(e)}"
        }), 500


# Endpoint para listar todas las fincas del usuario
@farm_bp.route('/api/fincas', methods=['GET'])
@jwt_required()
def list_farms():
    try:
        # Obtener el ID del usuario autenticado
        user_id = get_jwt_identity()

        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)

        # Consultar las fincas del usuario
        query = Farm.query.filter_by(usuario_id=user_id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Formatear los resultados
        farms_data = [farm.to_dict() for farm in pagination.items]

        # Retornar la respuesta JSON
        return jsonify({
            "success": True,
            "data": farms_data,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages,
            "message": "Fincas obtenidas exitosamente"
        }), 200

    except SQLAlchemyError as e:
        return jsonify({
            "error": True,
            "message": f"Error al listar las fincas: {str(e)}"
        }), 500