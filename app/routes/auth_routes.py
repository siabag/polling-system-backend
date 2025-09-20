# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user_model import User
from app.extensions import db
from app.models.role_model import Role

# Crear Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

# Endpoint para registrar un nuevo usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validar que se proporcionen los datos necesarios
        required_fields = ['nombre', 'apellido', 'correo', 'contrasena']
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

        # Obtener el rol_id del cuerpo de la solicitud (si no se proporciona, usar un valor predeterminado)
        rol_id = data.get('rol_id', 2)  # 2 es el ID del rol "encuestador" por defecto si no se especifica

        # Validar que el rol_id exista en la base de datos
        role = Role.query.get(rol_id)
        if not role:
            return jsonify({
                "error": True,
                "message": "El rol especificado no existe"
            }), 400

        # Crear un nuevo usuario
        hashed_password = generate_password_hash(data['contrasena'], method='pbkdf2:sha256')
        new_user = User(
            nombre=data['nombre'],
            apellido=data['apellido'],
            correo=data['correo'],
            contrasena_hash=hashed_password,
            rol_id=rol_id  # Asignar el rol_id proporcionado o el predeterminado
        )

        # Guardar el usuario en la base de datos
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": {
                "id": new_user.id,
                "nombre": new_user.nombre,
                "apellido": new_user.apellido,
                "correo": new_user.correo,
                "rol": role.nombre
            },
            "message": "Usuario registrado exitosamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": True,
            "message": f"Error al registrar el usuario: {str(e)}"
        }), 500

# Endpoint para listar todos los roles
@auth_bp.route('/roles', methods=['GET'])
def list_roles():
    try:
        roles = Role.query.all()
        roles_list = [{"id": role.id, "nombre": role.nombre} for role in roles]

        return jsonify({
            "success": True,
            "data": roles_list,
            "message": "Roles obtenidos exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener los roles: {str(e)}"
        }), 500

# Endpoint para iniciar sesión
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        # Validar que se proporcionen correo y contraseña
        correo = data.get('correo')
        contrasena = data.get('contrasena')
        if not correo or not contrasena:
            return jsonify({
                "error": True,
                "message": "Correo y contraseña son requeridos"
            }), 400

        # Buscar al usuario por correo
        user = User.query.filter_by(correo=correo).first()
        if not user or not check_password_hash(user.contrasena_hash, contrasena):
            return jsonify({
                "error": True,
                "message": "Credenciales inválidas"
            }), 401

        # Generar un token JWT
        access_token = create_access_token(identity=user.id)

        # Devolver el token y la información del usuario
        return jsonify({
            "success": True,
            "data": {
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "nombre": user.nombre,
                    "apellido": user.apellido,
                    "correo": user.correo,
                    "rol": user.rol.nombre
                }
            },
            "message": "Inicio de sesión exitoso"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al iniciar sesión: {str(e)}"
        }), 500


# Endpoint para cerrar sesión
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        return jsonify({
            "success": True,
            "message": "Sesión cerrada exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al cerrar sesión: {str(e)}"
        }), 500


# Endpoint para obtener información del usuario actual (protegido con JWT)
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                "error": True,
                "message": "Usuario no encontrado"
            }), 404

        # Devolver información del usuario
        return jsonify({
            "success": True,
            "data": {
                "id": user.id,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "correo": user.correo,
                "rol": user.rol.nombre
            },
            "message": "Información del usuario obtenida correctamente"
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Error al obtener la información del usuario: {str(e)}"
        }), 500