from .auth_routes import auth_bp
from .survey_routes import survey_bp
from .user_routes import user_bp
from .factor_routes import factor_bp
from .survey_type_routes import survey_type_bp
from .farm_routes import farm_bp
from .reports_routes import reports_bp
from .data_tth_routes import data_tth_bp

# Lista de blueprints para registrar
__all__ = [
    'auth_bp',
    'survey_bp',
    'user_bp',
    'factor_bp',
    'survey_type_bp',
    'farm_bp',
    'data_tth_bp'
]

# Función para registrar todos los blueprints en la aplicación
def register_routes(app):

    # Registro de Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(survey_bp)
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(factor_bp)
    app.register_blueprint(survey_type_bp)
    app.register_blueprint(farm_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(data_tth_bp)
