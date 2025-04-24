from flask import Flask
from .extensions import db, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)

    # Registrar blueprints
    from .routes.auth_routes import auth_bp
    from .routes.survey_routes import survey_bp
    from .routes.user_routes import user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app