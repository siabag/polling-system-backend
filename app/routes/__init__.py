from .auth_routes import auth_bp
from .survey_routes import survey_bp
from .user_routes import user_bp
from .factor_routes import factor_bp
from .survey_type_routes import survey_type_bp

# Lista de blueprints para registrar
__all__ = [
    'auth_bp',
    'survey_bp',
    'user_bp',
    'factor_bp',
    'survey_type_bp'
]

# Función para registrar todos los blueprints en la aplicación
def register_routes(app):

    # Registro de Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(factor_bp)
    app.register_blueprint(survey_type_bp)
