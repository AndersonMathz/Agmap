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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = '/tmp/uploads'  # Render usa /tmp para arquivos temporários
    ALLOWED_EXTENSIONS = {'kml', 'kmz', 'geojson'}
    
    # Configurações de rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Configurações de CORS
    CORS_ORIGINS = ['*']  # Liberado para desenvolvimento, restringir em produção
    
    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    @staticmethod
    def init_app(app):
        """Inicialização específica da configuração"""
        pass

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Desabilitar em desenvolvimento local

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Configurações específicas para Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Criar diretórios necessários
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Criar diretório de uploads se não existir
        upload_dir = os.path.join(app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Configurar logging para produção
        import logging
        logging.basicConfig(level=logging.INFO)

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 