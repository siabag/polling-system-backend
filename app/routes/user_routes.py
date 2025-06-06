# app/routes/user_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user_model import User
from app.extensions import db
from werkzeug.exceptions import NotFound, Forbidden

# Crear Blueprint para las rutas de usuarios
user_bp = Blueprint('user', __name__)

# Endpoint para obtener todos los usuarios (solo accesible para administradores)
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Verificar si el usuario tiene permisos de administrador
        if not current_user or current_user.rol.nombre != 'administrador':
            return jsonify({"error": True, "message": "Acceso denegado"}), 403

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

        return jsonify({
            "success": True,
            "data": result,
            "message": "Usuarios obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los usuarios: {str(e)}"
        }), 500


# Endpoint para actualizar la información de un usuario
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()

        # Verificar si el usuario está intentando actualizar su propia información o es administrador
        current_user = User.query.get(current_user_id)
        if not current_user or (current_user_id != user_id and current_user.rol.nombre != 'administrador'):
            return jsonify({"error": True, "message": "No tienes permiso para actualizar este usuario"}), 403

        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            raise NotFound("Usuario no encontrado")

        # Actualizar campos
        user.nombre = data.get('nombre', user.nombre)
        user.apellido = data.get('apellido', user.apellido)
        user.correo = data.get('correo', user.correo)

        # Guardar cambios
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Información de usuario actualizada exitosamente"
        }), 200

    except NotFound as e:
        return jsonify({
            "error": True,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al actualizar el usuario: {str(e)}"
        }), 500


# Endpoint para eliminar un usuario (solo accesible para administradores)
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Verificar si el usuario tiene permisos de administrador
        if not current_user or current_user.rol.nombre != 'administrador':
            return jsonify({"error": True, "message": "Acceso denegado"}), 403

        user = User.query.get(user_id)
        if not user:
            raise NotFound("Usuario no encontrado")

        # Eliminar el usuario
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Usuario eliminado exitosamente"
        }), 200

    except NotFound as e:
        return jsonify({
            "error": True,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al eliminar el usuario: {str(e)}"
        }), 500
    
from werkzeug.security import generate_password_hash

# Endpoint para crear un nuevo usuario
@user_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Validar que se proporcionen los datos necesarios
        required_fields = ['nombre', 'apellido', 'correo', 'contrasena', 'rol_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        if User.query.filter_by(correo=data['correo']).first():
            return jsonify({
                "error": True,
                "message": "El correo ya está registrado"
            }), 400

        # Crear un nuevo usuario
        hashed_password = generate_password_hash(data['contrasena'], method='sha256')
        new_user = User(
            nombre=data['nombre'],
            apellido=data['apellido'],
            correo=data['correo'],
            contrasena_hash=hashed_password,
            rol_id=data['rol_id'],
            activo=data.get('activo', True)  # Por defecto, el usuario está activo
        )

        # Guardar el usuario en la base de datos
        db.session.add(new_user)
        db.session.commit()

        # Devolver la respuesta con los detalles del usuario creado
        return jsonify({
            "success": True,
            "data": new_user.to_dict(),
            "message": "Usuario creado exitosamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear el usuario: {str(e)}"
        }), 500