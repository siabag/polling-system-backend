from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user_model import User
from app.extensions import db

# Crear Blueprint para las rutas de usuarios
user_bp = Blueprint('user', __name__)

# Endpoint para obtener todos los usuarios (solo accesible para administradores)
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # Verificar si el usuario tiene permisos de administrador
    if current_user.rol.nombre != 'administrador':
        return jsonify({"msg": "Acceso denegado"}), 403

    # Obtener todos los usuarios
    users = User.query.all()
    result = [
        {
            "id": user.id,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "correo": user.correo,
            "activo": user.activo,
            "rol": user.rol.nombre
        }
        for user in users
    ]

    return jsonify(result), 200

# Endpoint para actualizar la información de un usuario
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()

    # Verificar si el usuario está intentando actualizar su propia información
    if current_user_id != user_id:
        return jsonify({"msg": "No tienes permiso para actualizar este usuario"}), 403

    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # Actualizar campos
    user.nombre = data.get('nombre', user.nombre)
    user.apellido = data.get('apellido', user.apellido)
    user.correo = data.get('correo', user.correo)

    # Guardar cambios
    db.session.commit()

    return jsonify({"msg": "Información de usuario actualizada exitosamente"}), 200

# Endpoint para eliminar un usuario (solo accesible para administradores)
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # Verificar si el usuario tiene permisos de administrador
    if current_user.rol.nombre != 'administrador':
        return jsonify({"msg": "Acceso denegado"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # Eliminar el usuario
    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "Usuario eliminado exitosamente"}), 200