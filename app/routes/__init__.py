# app/routes/__init__.py

from .auth_routes import auth_bp
from .survey_routes import survey_bp
from .user_routes import user_bp

# Lista de blueprints para registrar
__all__ = [
    'auth_bp',
    'survey_bp',
    'user_routes'
]

# Función para registrar todos los blueprints en la aplicación
def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    app.register_blueprint(user_bp, url_prefix='/api/users')