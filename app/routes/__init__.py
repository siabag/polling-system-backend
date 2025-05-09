from .auth_routes import auth_bp
from .survey_routes import survey_bp
from .user_routes import user_bp
from .factor_routes import factor_bp
from .response_routes import response_bp 

# Lista de blueprints para registrar
__all__ = [
    'auth_bp',
    'survey_bp',
    'user_bp',
    'factor_bp',
    'response_bp' 
]

# Función para registrar todos los blueprints en la aplicación
def register_routes(app):

    # Registro de Blueprints con sus respectivos prefijos de URL
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(factor_bp, url_prefix='/api/factors')
    app.register_blueprint(response_bp, url_prefix='/api/responses')
