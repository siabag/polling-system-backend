# app/__init__.py

from flask import Flask
from .extensions import db, jwt  
from .config import Config  
from .routes import register_routes 

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)  
    jwt.init_app(app) 

    # Registrar blueprints (rutas)
    register_routes(app)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app