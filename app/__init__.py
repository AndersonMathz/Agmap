# -*- coding: utf-8 -*-
"""
WEBAG Professional - Aplicacao Flask
Inicializacao da aplicacao sem dependencias circulares
"""
import os
from flask import Flask

# SQLAlchemy sera importado apenas se disponivel
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    db = None
    SQLALCHEMY_AVAILABLE = False

def create_app(config_name='development'):
    """Factory para criar aplicacao Flask"""
    app = Flask(__name__)
    
    # Configurar aplicacao
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///instance/webgis.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Inicializar extensoes se disponivel
    if SQLALCHEMY_AVAILABLE and db:
        db.init_app(app)
    
    # Registrar blueprints (quando implementados)
    # from app.views import main_bp
    # app.register_blueprint(main_bp)
    
    return app