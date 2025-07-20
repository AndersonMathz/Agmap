import os
from datetime import datetime, timedelta

# Imports opcionais com fallbacks
try:
    from flask_sqlalchemy import SQLAlchemy
    SQLALCHEMY_AVAILABLE = True
    
    # Usar db global do app para evitar circular imports
    try:
        from app import db
    except ImportError:
        # Fallback para quando app não estiver disponível
        db = SQLAlchemy()
        
except ImportError:
    # Fallback quando SQLAlchemy não estiver disponível
    class MockDB:
        def __init__(self):
            pass
        class Model:
            pass
        Column = None
        Integer = None
        String = None
        JSON = None
    db = MockDB()
    SQLALCHEMY_AVAILABLE = False

# Imports opcionais com fallbacks
try:
    from flask_login import UserMixin
    FLASK_LOGIN_AVAILABLE = True
except ImportError:
    FLASK_LOGIN_AVAILABLE = False

try:
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    WERKZEUG_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Definir classe base User
if FLASK_LOGIN_AVAILABLE:
    BaseUser = UserMixin
else:
    class BaseUser:
        """Classe base para usuário sem Flask-Login"""
        def __init__(self):
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
        
        def get_id(self):
            return self.id

class User(BaseUser):
    """Modelo de usuário com autenticação segura"""
    
    def __init__(self, username, password_hash, role='user', name='', privileges=None):
        super().__init__()
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.name = name
        self.privileges = privileges or {}
        self.id = username  # Para Flask-Login
    
    @staticmethod
    def create_user(username, password, role='user', name='', privileges=None):
        """Criar novo usuário com senha criptografada"""
        if WERKZEUG_AVAILABLE:
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        else:
            # Fallback simples se werkzeug não estiver disponível
            password_hash = f"hash_{password}"  # Não usar em produção!
        return User(username, password_hash, role, name, privileges)
    
    def check_password(self, password):
        """Verificar senha de forma segura"""
        if WERKZEUG_AVAILABLE:
            return check_password_hash(self.password_hash, password)
        else:
            # Fallback simples - não usar em produção!
            return self.password_hash == f"hash_{password}"
    
    def has_privilege(self, privilege):
        """Verificar se usuário tem determinado privilégio"""
        return self.privileges.get(privilege, False)
    
    def is_superuser(self):
        """Verificar se é superusuário"""
        return self.role == 'superuser'
    
    def generate_token(self, secret_key, expires_in=3600):
        """Gerar token JWT para autenticação"""
        if JWT_AVAILABLE:
            payload = {
                'username': self.username,
                'role': self.role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow()
            }
            return jwt.encode(payload, secret_key, algorithm='HS256')
        else:
            return None
    
    @staticmethod
    def verify_token(token, secret_key):
        """Verificar e decodificar token JWT"""
        if JWT_AVAILABLE:
            try:
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                return payload
            except jwt.ExpiredSignatureError:
                return None
            except jwt.InvalidTokenError:
                return None
        else:
            return None

# Banco de dados em memória (para produção, use um banco real)
users_db = {}

if SQLALCHEMY_AVAILABLE:
    class GeoFeature(db.Model):
        __tablename__ = 'geofeatures'
        id = db.Column(db.Integer, primary_key=True)
        layer_name = db.Column(db.String(100), nullable=False)
        geometry = db.Column(db.JSON, nullable=False)
        properties = db.Column(db.JSON, nullable=False)

        def to_dict(self):
            """Converte o objeto para um dicionário (formato GeoJSON Feature)"""
            feature_properties = self.properties.copy()
            feature_properties['layer_name'] = self.layer_name
            
            return {
                'type': 'Feature',
                'id': self.id,
                'geometry': self.geometry,
                'properties': feature_properties
            }

    class Gleba(db.Model):
        __tablename__ = 'glebas'
        id = db.Column(db.Integer, primary_key=True)
        
        # Informações básicas da gleba
        no_gleba = db.Column(db.String(50), nullable=False)
        nome_gleba = db.Column(db.String(100), nullable=True)
        area = db.Column(db.Float, nullable=True)  # em m²
        perimetro = db.Column(db.Float, nullable=True)  # em m
        
        # Geometria da gleba
        geometry = db.Column(db.JSON, nullable=False)  # GeoJSON geometry
        
        # Informações do proprietário
        proprietario = db.Column(db.String(100), nullable=True)
        cpf = db.Column(db.String(14), nullable=True)  # 000.000.000-00
        rg = db.Column(db.String(20), nullable=True)
        
        # Endereço
        rua = db.Column(db.String(200), nullable=True)
        bairro = db.Column(db.String(100), nullable=True)
        quadra = db.Column(db.String(50), nullable=True)
        cep = db.Column(db.String(9), nullable=True)  # 00000-000
        cidade = db.Column(db.String(100), nullable=True)
        uf = db.Column(db.String(2), nullable=True)
        
        # Testadas
        testada_frente = db.Column(db.Float, nullable=True)
        testada_fundo = db.Column(db.Float, nullable=True)
        testada_esquerda = db.Column(db.Float, nullable=True)
        testada_direita = db.Column(db.Float, nullable=True)
        
        # Confrontações
        confrontacao_frente = db.Column(db.String(200), nullable=True)
        confrontacao_fundo = db.Column(db.String(200), nullable=True)
        confrontacao_esquerda = db.Column(db.String(200), nullable=True)
        confrontacao_direita = db.Column(db.String(200), nullable=True)
        
        # Imóvel
        valor_imovel = db.Column(db.Float, nullable=True)
        matricula = db.Column(db.String(50), nullable=True)
        inscricao_municipal = db.Column(db.String(50), nullable=True)
        
        # Observações
        observacoes = db.Column(db.Text, nullable=True)
        
        # Metadados
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        created_by = db.Column(db.String(50), nullable=True)

        def to_dict(self):
            """Converte a gleba para dicionário"""
            return {
                'id': self.id,
                'no_gleba': self.no_gleba,
                'nome_gleba': self.nome_gleba,
                'area': self.area,
                'perimetro': self.perimetro,
                'geometry': self.geometry,
                'proprietario': self.proprietario,
                'cpf': self.cpf,
                'rg': self.rg,
                'rua': self.rua,
                'bairro': self.bairro,
                'quadra': self.quadra,
                'cep': self.cep,
                'cidade': self.cidade,
                'uf': self.uf,
                'testada_frente': self.testada_frente,
                'testada_fundo': self.testada_fundo,
                'testada_esquerda': self.testada_esquerda,
                'testada_direita': self.testada_direita,
                'confrontacao_frente': self.confrontacao_frente,
                'confrontacao_fundo': self.confrontacao_fundo,
                'confrontacao_esquerda': self.confrontacao_esquerda,
                'confrontacao_direita': self.confrontacao_direita,
                'valor_imovel': self.valor_imovel,
                'matricula': self.matricula,
                'inscricao_municipal': self.inscricao_municipal,
                'observacoes': self.observacoes,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'created_by': self.created_by
            }

        def to_geojson(self):
            """Converte a gleba para formato GeoJSON Feature"""
            properties = self.to_dict()
            # Remove geometry do properties para evitar duplicação
            geometry = properties.pop('geometry')
            
            return {
                'type': 'Feature',
                'id': self.id,
                'geometry': geometry,
                'properties': properties
            }
else:
    class GeoFeature:
        """Fallback class quando SQLAlchemy não disponível"""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def to_dict(self):
            """Converte o objeto para um dicionário (formato GeoJSON Feature)"""
            feature_properties = getattr(self, 'properties', {}).copy()
            feature_properties['layer_name'] = getattr(self, 'layer_name', '')
            
            return {
                'type': 'Feature',
                'id': getattr(self, 'id', None),
                'geometry': getattr(self, 'geometry', None),
                'properties': feature_properties
            }

def init_users():
    """Inicializar usuários padrão"""
    global users_db
    
    # Superusuário
    superuser = User.create_user(
        username='admin_super',
        password=os.environ.get('ADMIN_PASSWORD', 'TempPassword123!'),
        role='superuser',
        name='Administrador',
        privileges={
            'canEditLayers': True,
            'canManageUsers': True,
            'canExportData': True,
            'canViewAllData': True,
            'canModifyStyles': True,
            'canDeleteFeatures': True,
            'canAddNewLayers': True,
            'canUploadFiles': True
        }
    )
    
    # Usuário padrão
    user = User.create_user(
        username='admin',
        password='admin',
        role='user',
        name='Usuário Padrão',
        privileges={
            'canEditLayers': False,
            'canManageUsers': False,
            'canExportData': False,
            'canViewAllData': True,
            'canModifyStyles': False,
            'canDeleteFeatures': False,
            'canAddNewLayers': False,
            'canUploadFiles': False
        }
    )
    
    users_db['admin_super'] = superuser
    users_db['admin'] = user

def get_user_by_username(username):
    """Buscar usuário por username"""
    return users_db.get(username)

def authenticate_user(username, password):
    """Autenticar usuário"""
    user = get_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None 