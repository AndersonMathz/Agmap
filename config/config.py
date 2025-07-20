import os

# Tentar carregar dotenv se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Se dotenv não estiver disponível, continuar sem ele
    pass

class Config:
    """Configurações de segurança para o WebGIS"""
    
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'kml', 'kmz'}
    
    # Configurações de rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Configurações de CORS
    CORS_ORIGINS = ['https://seudominio.com']  # Configure seu domínio
    
    # Configurações de banco de dados (se necessário)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///webgis.db'

    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///webgis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Desabilitar em desenvolvimento local

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 