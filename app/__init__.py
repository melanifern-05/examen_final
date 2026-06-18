# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # <--- AGREGA ESTA LÍNEA
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()  # <--- AGREGA ESTA LÍNEA

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)  # <--- AGREGA ESTA LÍNEA
    
    # Registro de tus Blueprints...
    from app.dashboard.routes import dashboard_bp
    from app.data.routes import data_bp
    from app.auth.routes import auth_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(auth_bp)
    
    return app