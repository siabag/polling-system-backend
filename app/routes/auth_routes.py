from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user_model import User
from app.extensions import db
from app.models import Role

# Crear Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

# Endpoint para registrar un nuevo usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validar que se proporcionen los datos necesarios
    if not data or not data.get('nombre') or not data.get('apellido') or not data.get('correo') or not data.get('contrasena'):
        return jsonify({"msg": "Faltan datos requeridos"}), 400

    # Verificar si el correo ya está registrado
    if User.query.filter_by(correo=data['correo']).first():
        return jsonify({"msg": "El correo ya está registrado"}), 400

    # Obtener el rol_id del cuerpo de la solicitud (si no se proporciona, usar un valor predeterminado)
    rol_id = data.get('rol_id', 2)  # 2 es el ID del rol "encuestador" por defecto si no se especifica

    # Validar que el rol_id exista en la base de datos
    role = Role.query.get(rol_id)
    if not role:
        return jsonify({"msg": "El rol especificado no existe"}), 400

    # Crear un nuevo usuario
    hashed_password = generate_password_hash(data['contrasena'], method='sha256')
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

    return jsonify({"msg": "Usuario registrado exitosamente", "rol_asignado": role.nombre}), 201

# Endpoint para iniciar sesión
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validar que se proporcionen correo y contraseña
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    if not correo or not contrasena:
        return jsonify({"msg": "Correo y contraseña son requeridos"}), 400

    # Buscar al usuario por correo
    user = User.query.filter_by(correo=correo).first()
    if not user or not check_password_hash(user.contrasena_hash, contrasena):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # Generar un token JWT
    access_token = create_access_token(identity=user.id)
    
    # Devolver el token y la información del usuario
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "correo": user.correo,
            "rol": user.rol.nombre
        }
    }), 200

# Endpoint para cerrar sesión
@auth_bp.route('/logout', methods=['POST'])
@jwt_required() 
def logout():
    return jsonify({"msg": "Sesión cerrada exitosamente"}), 200

# Endpoint para obtener información del usuario actual (protegido con JWT)
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # Devolver información del usuario
    return jsonify({
        "id": user.id,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "correo": user.correo,
        "rol": user.rol.nombre
    }), 200