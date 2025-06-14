# app/services/auth_service.py

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_model import User
from app.models.role_model import Role
from app.extensions import db

def register_user(data):
    try:
        # Validar que se proporcionen los datos necesarios
        required_fields = ['nombre', 'apellido', 'correo', 'contrasena']
        if not all(field in data for field in required_fields):
            return {"error": "Faltan datos requeridos"}, 400

        # Verificar si el correo ya está registrado
        if User.query.filter_by(correo=data['correo']).first():
            return {"error": "El correo ya está registrado"}, 400

        # Obtener el rol_id del cuerpo de la solicitud (si no se proporciona, usar un valor predeterminado)
        rol_id = data.get('rol_id', 2)  # 2 es el ID del rol "encuestador" por defecto si no se especifica

        # Validar que el rol_id exista en la base de datos
        role = Role.query.get(rol_id)
        if not role:
            return {"error": "El rol especificado no existe"}, 400

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

        return {"msg": "Usuario registrado exitosamente", "rol_asignado": role.nombre}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al registrar el usuario: {str(e)}"}, 500


def authenticate_user(correo, contrasena):
    try:
        # Buscar al usuario por correo
        user = User.query.filter_by(correo=correo).first()
        if not user:
            return {"error": "Credenciales inválidas"}, 401

        # Verificar la contraseña
        if not check_password_hash(user.contrasena_hash, contrasena):
            return {"error": "Credenciales inválidas"}, 401

        # Devolver información del usuario autenticado
        return {"user_id": user.id, "nombre": user.nombre, "apellido": user.apellido, "rol": user.rol.nombre}, 200

    except Exception as e:
        return {"error": f"Error al autenticar el usuario: {str(e)}"}, 500