# app/services/permission_service.py

from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user_model import User

def role_required(role_name):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {"error": "Usuario no encontrado"}, 404

            if user.rol.nombre != role_name:
                return {"error": "Acceso denegado"}, 403

            return func(*args, **kwargs)
        return wrapper
    return decorator