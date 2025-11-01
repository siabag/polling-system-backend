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

        # Obtener parámetros de filtro de la query string
        rol_filter = request.args.get('rol')
        activo_filter = request.args.get('activo')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Construir query base
        query = User.query

        # Aplicar filtro por rol si se proporciona
        if rol_filter:
            query = query.join(User.rol).filter_by(nombre=rol_filter)

        # Aplicar filtro por estado activo/inactivo si se proporciona
        if activo_filter is not None:
            activo_bool = activo_filter.lower() == 'true'
            query = query.filter_by(activo=activo_bool)

        # Aplicar búsqueda por nombre, apellido o correo si se proporciona
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.nombre.ilike(search_term),
                    User.apellido.ilike(search_term),
                    User.correo.ilike(search_term)
                )
            )

        # Contar total de usuarios con filtros aplicados
        total = query.count()

        # Aplicar paginación
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()

        # Formatear resultado
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
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit,
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
    
from werkzeug.security import generate_password_hash, check_password_hash

# Endpoint para crear un nuevo usuario (solo accesible para administradores)
@user_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    try:
        # Obtener el ID del usuario autenticado
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Verificar si el usuario tiene permisos de administrador
        if not current_user or current_user.rol.nombre != 'administrador':
            return jsonify({
                "error": True,
                "message": "Acceso denegado. Solo los administradores pueden crear usuarios."
            }), 403

        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Validar que se proporcionen los datos necesarios
        required_fields = ['nombre', 'apellido', 'correo', 'contrasena', 'rol_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": True,
                "message": "Faltan datos requeridos"
            }), 400

        # Verificar si el correo ya está registrado
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
        # Manejar errores inesperados
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al crear el usuario: {str(e)}"
        }), 500


# Endpoint para cambiar la contraseña de un usuario
@user_bp.route('/users/<int:user_id>/change-password', methods=['POST'])
@jwt_required()
def change_password(user_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar si el usuario está intentando cambiar su propia contraseña o es administrador
        current_user = User.query.get(current_user_id)
        if not current_user or (current_user_id != user_id and current_user.rol.nombre != 'administrador'):
            return jsonify({
                "error": True,
                "message": "No tienes permiso para cambiar la contraseña de este usuario"
            }), 403

        data = request.get_json()
        
        # Validar que se proporcionen los datos necesarios
        if 'contrasenaActual' not in data or 'nuevaContrasena' not in data:
            return jsonify({
                "error": True,
                "message": "Se requiere la contraseña actual y la nueva contraseña"
            }), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "error": True,
                "message": "Usuario no encontrado"
            }), 404

        # Verificar que la contraseña actual sea correcta (solo si el usuario cambia su propia contraseña)
        if current_user_id == user_id:
            if not check_password_hash(user.contrasena_hash, data['contrasenaActual']):
                return jsonify({
                    "error": True,
                    "message": "La contraseña actual es incorrecta"
                }), 400

        # Validar longitud de la nueva contraseña
        if len(data['nuevaContrasena']) < 6:
            return jsonify({
                "error": True,
                "message": "La nueva contraseña debe tener al menos 6 caracteres"
            }), 400

        # Actualizar la contraseña
        user.contrasena_hash = generate_password_hash(data['nuevaContrasena'], method='sha256')
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Contraseña actualizada exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al cambiar la contraseña: {str(e)}"
        }), 500
