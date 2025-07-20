"""
WEBAG Professional - Enhanced Database Models
Sistema robusto de modelos com gestão avançada de camadas
"""

import os
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any

# Imports opcionais com fallbacks
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import event, text
    from sqlalchemy.ext.hybrid import hybrid_property
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import validates
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

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

# Import do db global
try:
    from app import db
except ImportError:
    if SQLALCHEMY_AVAILABLE:
        db = SQLAlchemy()
    else:
        db = None

# ================================================
# ENUMS E CONSTANTES
# ================================================

class ProjectType(Enum):
    TOPOGRAPHY = "topography"
    CADASTRE = "cadastre" 
    PLANNING = "planning"
    ENVIRONMENTAL = "environmental"

class LayerType(Enum):
    VECTOR = "vector"
    RASTER = "raster"
    WMS = "wms"
    WFS = "wfs"
    GEOJSON = "geojson"
    TILE = "tile"

class GeometryType(Enum):
    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLineString"
    MULTIPOLYGON = "MultiPolygon"

class StatusType(Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    ARCHIVED = "archived"
    DELETED = "deleted"

class OperationType(Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

# ================================================
# BASE CLASSES
# ================================================

class BaseModel:
    """Classe base com funcionalidades comuns"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte modelo para dicionário"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Enum):
                value = value.value
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Atualiza modelo a partir de dicionário"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

if FLASK_LOGIN_AVAILABLE:
    BaseUser = UserMixin
else:
    class BaseUser:
        def __init__(self):
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
        def get_id(self):
            return self.id

# ================================================
# CORE MODELS
# ================================================

if SQLALCHEMY_AVAILABLE:
    
    class Organization(BaseModel, db.Model):
        """Modelo de Organização (Multi-tenant)"""
        __tablename__ = 'organizations'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        name = db.Column(db.String(255), nullable=False, unique=True)
        slug = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.Text)
        logo_url = db.Column(db.String(500))
        settings = db.Column(db.JSON, default=dict)
        subscription_plan = db.Column(db.String(50), default='free')
        max_users = db.Column(db.Integer, default=10)
        max_projects = db.Column(db.Integer, default=5)
        max_storage_mb = db.Column(db.Integer, default=1000)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relacionamentos
        users = db.relationship('User', backref='organization', lazy='dynamic', cascade='all, delete-orphan')
        projects = db.relationship('Project', backref='organization', lazy='dynamic', cascade='all, delete-orphan')
        
        @validates('slug')
        def validate_slug(self, key, slug):
            """Validar formato do slug"""
            import re
            if not re.match(r'^[a-z0-9-]+$', slug):
                raise ValueError("Slug deve conter apenas letras minúsculas, números e hífens")
            return slug
        
        def can_add_user(self) -> bool:
            """Verificar se pode adicionar mais usuários"""
            return self.users.count() < self.max_users
        
        def can_add_project(self) -> bool:
            """Verificar se pode adicionar mais projetos"""
            return self.projects.count() < self.max_projects

    class User(BaseUser, BaseModel, db.Model):
        """Modelo de Usuário (Enhanced)"""
        __tablename__ = 'users'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        organization_id = db.Column(db.String(32), db.ForeignKey('organizations.id'), nullable=False)
        username = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(255), nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        first_name = db.Column(db.String(100))
        last_name = db.Column(db.String(100))
        role = db.Column(db.String(50), default='user')
        privileges = db.Column(db.JSON, default=dict)
        avatar_url = db.Column(db.String(500))
        last_login_at = db.Column(db.DateTime)
        login_count = db.Column(db.Integer, default=0)
        is_active = db.Column(db.Boolean, default=True)
        email_verified = db.Column(db.Boolean, default=False)
        two_factor_enabled = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Constraint único por organização
        __table_args__ = (
            db.UniqueConstraint('organization_id', 'username'),
            db.UniqueConstraint('organization_id', 'email'),
        )
        
        # Relacionamentos
        owned_projects = db.relationship('Project', backref='owner', lazy='dynamic')
        created_layers = db.relationship('Layer', foreign_keys='Layer.created_by', backref='creator', lazy='dynamic')
        
        @hybrid_property
        def full_name(self):
            """Nome completo do usuário"""
            if self.first_name and self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.username
        
        def set_password(self, password: str):
            """Definir senha de forma segura"""
            if WERKZEUG_AVAILABLE:
                self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            else:
                self.password_hash = f"hash_{password}"
        
        def check_password(self, password: str) -> bool:
            """Verificar senha"""
            if WERKZEUG_AVAILABLE:
                return check_password_hash(self.password_hash, password)
            return self.password_hash == f"hash_{password}"
        
        def has_privilege(self, privilege: str) -> bool:
            """Verificar privilégio específico"""
            return self.privileges.get(privilege, False)
        
        def is_superuser(self) -> bool:
            """Verificar se é superusuário"""
            return self.role == 'superuser'
        
        def record_login(self):
            """Registrar login do usuário"""
            self.last_login_at = datetime.utcnow()
            self.login_count += 1

    class Project(BaseModel, db.Model):
        """Modelo de Projeto (Enhanced)"""
        __tablename__ = 'projects'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        organization_id = db.Column(db.String(32), db.ForeignKey('organizations.id'), nullable=False)
        name = db.Column(db.String(255), nullable=False)
        slug = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        project_type = db.Column(db.Enum(ProjectType), default=ProjectType.TOPOGRAPHY)
        bbox_coordinates = db.Column(db.JSON)  # [minX, minY, maxX, maxY]
        default_projection = db.Column(db.String(20), default='EPSG:4326')
        thumbnail_url = db.Column(db.String(500))
        settings = db.Column(db.JSON, default=dict)
        status = db.Column(db.Enum(StatusType), default=StatusType.ACTIVE)
        owner_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
        visibility = db.Column(db.String(20), default='private')  # public, private, organization
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        __table_args__ = (
            db.UniqueConstraint('organization_id', 'slug'),
        )
        
        # Relacionamentos
        layer_groups = db.relationship('LayerGroup', backref='project', lazy='dynamic', cascade='all, delete-orphan')
        layers = db.relationship('Layer', backref='project', lazy='dynamic', cascade='all, delete-orphan')
        glebas = db.relationship('Gleba', backref='project', lazy='dynamic', cascade='all, delete-orphan')
        
        @validates('slug')
        def validate_slug(self, key, slug):
            """Validar formato do slug"""
            import re
            if not re.match(r'^[a-z0-9-]+$', slug):
                raise ValueError("Slug deve conter apenas letras minúsculas, números e hífens")
            return slug
        
        def get_bbox(self) -> Optional[List[float]]:
            """Obter bounding box do projeto"""
            if self.bbox_coordinates:
                return self.bbox_coordinates
            
            # Calcular bbox a partir das layers
            # TODO: Implementar cálculo automático
            return None

    # ================================================
    # LAYER MANAGEMENT MODELS
    # ================================================

    class LayerGroup(BaseModel, db.Model):
        """Modelo de Grupo de Camadas"""
        __tablename__ = 'layer_groups'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        project_id = db.Column(db.String(32), db.ForeignKey('projects.id'), nullable=False)
        parent_group_id = db.Column(db.String(32), db.ForeignKey('layer_groups.id'))
        name = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text)
        display_order = db.Column(db.Integer, default=0)
        is_expanded = db.Column(db.Boolean, default=True)
        is_visible = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relacionamentos hierárquicos
        children = db.relationship('LayerGroup', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
        layers = db.relationship('Layer', backref='layer_group', lazy='dynamic')
        
        def get_all_children(self) -> List['LayerGroup']:
            """Obter todos os grupos filhos recursivamente"""
            children = []
            for child in self.children:
                children.append(child)
                children.extend(child.get_all_children())
            return children

    class Layer(BaseModel, db.Model):
        """Modelo de Camada (Enhanced)"""
        __tablename__ = 'layers'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        project_id = db.Column(db.String(32), db.ForeignKey('projects.id'), nullable=False)
        layer_group_id = db.Column(db.String(32), db.ForeignKey('layer_groups.id'))
        name = db.Column(db.String(255), nullable=False)
        display_name = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text)
        layer_type = db.Column(db.Enum(LayerType), nullable=False)
        geometry_type = db.Column(db.Enum(GeometryType))
        source_type = db.Column(db.String(50), default='internal')
        source_url = db.Column(db.String(1000))
        source_config = db.Column(db.JSON, default=dict)
        
        # Configurações visuais
        default_style = db.Column(db.JSON, default=dict)
        min_zoom = db.Column(db.Integer, default=0)
        max_zoom = db.Column(db.Integer, default=18)
        opacity = db.Column(db.Float, default=1.0)
        
        # Metadados
        srid = db.Column(db.String(20), default='EPSG:4326')
        bbox_coordinates = db.Column(db.JSON)
        feature_count = db.Column(db.Integer, default=0)
        file_size_bytes = db.Column(db.Integer, default=0)
        schema_definition = db.Column(db.JSON, default=dict)
        
        # Controle de acesso
        is_public = db.Column(db.Boolean, default=False)
        is_editable = db.Column(db.Boolean, default=True)
        is_deletable = db.Column(db.Boolean, default=True)
        edit_permissions = db.Column(db.JSON, default=dict)
        
        # Status e ordem
        status = db.Column(db.Enum(StatusType), default=StatusType.ACTIVE)
        display_order = db.Column(db.Integer, default=0)
        is_visible = db.Column(db.Boolean, default=True)
        is_selectable = db.Column(db.Boolean, default=True)
        
        # Auditoria
        created_by = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
        updated_by = db.Column(db.String(32), db.ForeignKey('users.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        __table_args__ = (
            db.UniqueConstraint('project_id', 'name'),
        )
        
        # Relacionamentos
        features = db.relationship('Feature', backref='layer', lazy='dynamic', cascade='all, delete-orphan')
        versions = db.relationship('LayerVersion', backref='layer', lazy='dynamic', cascade='all, delete-orphan')
        
        @validates('opacity')
        def validate_opacity(self, key, opacity):
            """Validar opacidade"""
            if not 0 <= opacity <= 1:
                raise ValueError("Opacidade deve estar entre 0 e 1")
            return opacity
        
        def get_default_style(self) -> Dict[str, Any]:
            """Obter estilo padrão baseado no tipo de geometria"""
            default_styles = {
                GeometryType.POINT: {
                    "color": "#3388ff",
                    "fillColor": "#3388ff",
                    "fillOpacity": 0.7,
                    "radius": 5,
                    "weight": 2
                },
                GeometryType.LINESTRING: {
                    "color": "#3388ff",
                    "weight": 3,
                    "opacity": 0.8
                },
                GeometryType.POLYGON: {
                    "color": "#3388ff",
                    "fillColor": "#3388ff",
                    "fillOpacity": 0.2,
                    "weight": 2,
                    "opacity": 0.8
                }
            }
            
            if self.default_style:
                return self.default_style
            
            return default_styles.get(self.geometry_type, default_styles[GeometryType.POINT])
        
        def can_edit(self, user: User) -> bool:
            """Verificar se usuário pode editar a camada"""
            if not self.is_editable:
                return False
            
            if user.is_superuser():
                return True
            
            if self.created_by == user.id:
                return True
            
            return user.has_privilege('canEditLayers')
        
        def create_version(self, version_name: str, description: str, user: User) -> 'LayerVersion':
            """Criar nova versão da camada"""
            version_number = self.versions.count() + 1
            
            layer_config = {
                'layer_data': self.to_dict(),
                'features': [f.to_dict() for f in self.features.filter_by(is_current=True)],
                'created_at': datetime.utcnow().isoformat()
            }
            
            version = LayerVersion(
                layer_id=self.id,
                version_number=version_number,
                version_name=version_name,
                description=description,
                layer_config=layer_config,
                feature_count=self.feature_count,
                created_by=user.id
            )
            
            return version

    class Feature(BaseModel, db.Model):
        """Modelo de Feature Geográfica (Enhanced)"""
        __tablename__ = 'features'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        layer_id = db.Column(db.String(32), db.ForeignKey('layers.id'), nullable=False)
        feature_type = db.Column(db.Enum(GeometryType), nullable=False)
        geometry = db.Column(db.JSON, nullable=False)
        properties = db.Column(db.JSON, default=dict)
        style_override = db.Column(db.JSON, default=dict)
        
        # Metadados calculados
        area_m2 = db.Column(db.Float)
        length_m = db.Column(db.Float)
        perimeter_m = db.Column(db.Float)
        centroid_coordinates = db.Column(db.JSON)
        
        # Versionamento
        version = db.Column(db.Integer, default=1)
        is_current = db.Column(db.Boolean, default=True)
        parent_feature_id = db.Column(db.String(32), db.ForeignKey('features.id'))
        
        # Status
        status = db.Column(db.Enum(StatusType), default=StatusType.ACTIVE)
        validation_status = db.Column(db.String(20), default='valid')
        validation_errors = db.Column(db.JSON)
        
        # Auditoria
        created_by = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
        updated_by = db.Column(db.String(32), db.ForeignKey('users.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relacionamentos
        children = db.relationship('Feature', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
        gleba = db.relationship('Gleba', backref='feature', uselist=False, cascade='all, delete-orphan')
        
        def to_geojson(self) -> Dict[str, Any]:
            """Converter para formato GeoJSON"""
            properties = self.properties.copy()
            properties.update({
                'id': self.id,
                'layer_id': self.layer_id,
                'feature_type': self.feature_type.value,
                'area_m2': self.area_m2,
                'length_m': self.length_m,
                'perimeter_m': self.perimeter_m,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
            
            return {
                'type': 'Feature',
                'id': self.id,
                'geometry': self.geometry,
                'properties': properties
            }
        
        def calculate_metrics(self):
            """Calcular métricas geométricas"""
            # TODO: Implementar cálculos baseados na geometria
            # Por enquanto, placeholder
            if self.feature_type == GeometryType.POLYGON:
                # Calcular área e perímetro
                pass
            elif self.feature_type == GeometryType.LINESTRING:
                # Calcular comprimento
                pass

    # ================================================
    # SPECIALIZED MODELS
    # ================================================

    class Gleba(BaseModel, db.Model):
        """Modelo de Gleba (Enhanced para Topografia)"""
        __tablename__ = 'glebas'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        project_id = db.Column(db.String(32), db.ForeignKey('projects.id'), nullable=False)
        feature_id = db.Column(db.String(32), db.ForeignKey('features.id'), nullable=False, unique=True)
        
        # Identificação
        numero_gleba = db.Column(db.String(50), nullable=False)
        nome_gleba = db.Column(db.String(255))
        tipo_gleba = db.Column(db.String(50), default='urbana')
        
        # Medições (calculadas automaticamente)
        area_total_m2 = db.Column(db.Float)
        area_construida_m2 = db.Column(db.Float)
        perimetro_total_m = db.Column(db.Float)
        
        # Testadas (calculadas automaticamente)
        testada_frente_m = db.Column(db.Float)
        testada_fundo_m = db.Column(db.Float)
        testada_esquerda_m = db.Column(db.Float)
        testada_direita_m = db.Column(db.Float)
        
        # Confrontações
        confrontacao_frente = db.Column(db.Text)
        confrontacao_fundo = db.Column(db.Text)
        confrontacao_esquerda = db.Column(db.Text)
        confrontacao_direita = db.Column(db.Text)
        
        # Proprietário
        proprietario_nome = db.Column(db.String(255))
        proprietario_cpf_cnpj = db.Column(db.String(18))
        proprietario_rg = db.Column(db.String(20))
        proprietario_email = db.Column(db.String(255))
        proprietario_telefone = db.Column(db.String(20))
        
        # Endereço
        endereco_logradouro = db.Column(db.String(300))
        endereco_numero = db.Column(db.String(20))
        endereco_complemento = db.Column(db.String(100))
        endereco_bairro = db.Column(db.String(100))
        endereco_cidade = db.Column(db.String(100))
        endereco_uf = db.Column(db.String(2))
        endereco_cep = db.Column(db.String(9))
        endereco_quadra = db.Column(db.String(50))
        endereco_lote = db.Column(db.String(50))
        
        # Informações Legais
        matricula_registro = db.Column(db.String(100))
        cartorio_registro = db.Column(db.String(255))
        inscricao_municipal = db.Column(db.String(100))
        inscricao_estadual = db.Column(db.String(100))
        iptu_numero = db.Column(db.String(100))
        
        # Informações Financeiras
        valor_venal = db.Column(db.Float)
        valor_mercado = db.Column(db.Float)
        valor_iptu = db.Column(db.Float)
        
        # Uso do Solo
        uso_atual = db.Column(db.String(100))
        uso_permitido = db.Column(db.String(100))
        zoneamento = db.Column(db.String(50))
        coeficiente_aproveitamento = db.Column(db.Float)
        taxa_ocupacao = db.Column(db.Float)
        
        # Observações
        observacoes = db.Column(db.Text)
        anotacoes_tecnicas = db.Column(db.Text)
        
        # Status e Validação
        status_aprovacao = db.Column(db.String(20), default='rascunho')
        validado_por = db.Column(db.String(32), db.ForeignKey('users.id'))
        validado_em = db.Column(db.DateTime)
        
        # Auditoria
        created_by = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
        updated_by = db.Column(db.String(32), db.ForeignKey('users.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        __table_args__ = (
            db.UniqueConstraint('project_id', 'numero_gleba'),
        )
        
        # Relacionamentos
        validador = db.relationship('User', foreign_keys=[validado_por])
        
        def to_geojson(self) -> Dict[str, Any]:
            """Converter para formato GeoJSON completo"""
            return {
                'type': 'Feature',
                'id': self.id,
                'geometry': self.feature.geometry if self.feature else None,
                'properties': {
                    'numero_gleba': self.numero_gleba,
                    'nome_gleba': self.nome_gleba,
                    'tipo_gleba': self.tipo_gleba,
                    'area_total_m2': self.area_total_m2,
                    'perimetro_total_m': self.perimetro_total_m,
                    'proprietario_nome': self.proprietario_nome,
                    'endereco_completo': self.get_endereco_completo(),
                    'valor_venal': self.valor_venal,
                    'status_aprovacao': self.status_aprovacao,
                    'created_at': self.created_at.isoformat() if self.created_at else None
                }
            }
        
        def get_endereco_completo(self) -> str:
            """Obter endereço completo formatado"""
            partes = []
            if self.endereco_logradouro:
                partes.append(self.endereco_logradouro)
            if self.endereco_numero:
                partes.append(self.endereco_numero)
            if self.endereco_bairro:
                partes.append(self.endereco_bairro)
            if self.endereco_cidade:
                partes.append(self.endereco_cidade)
            if self.endereco_uf:
                partes.append(self.endereco_uf)
            return ', '.join(partes)
        
        def calcular_testadas(self):
            """Calcular testadas automaticamente baseado na geometria"""
            if not self.feature or not self.feature.geometry:
                return
            
            # TODO: Implementar algoritmo de cálculo de testadas
            # Usar algoritmo do app.py existente
            pass

    # ================================================
    # AUDIT & VERSIONING MODELS
    # ================================================

    class AuditLog(BaseModel, db.Model):
        """Modelo de Log de Auditoria"""
        __tablename__ = 'audit_log'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        table_name = db.Column(db.String(100), nullable=False)
        record_id = db.Column(db.String(32), nullable=False)
        operation = db.Column(db.Enum(OperationType), nullable=False)
        old_values = db.Column(db.JSON)
        new_values = db.Column(db.JSON)
        changed_fields = db.Column(db.JSON)
        user_id = db.Column(db.String(32), db.ForeignKey('users.id'))
        user_ip = db.Column(db.String(45))
        user_agent = db.Column(db.Text)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Relacionamentos
        user = db.relationship('User', backref='audit_logs')

    class LayerVersion(BaseModel, db.Model):
        """Modelo de Versão de Camada"""
        __tablename__ = 'layer_versions'
        
        id = db.Column(db.String(32), primary_key=True, default=lambda: os.urandom(16).hex())
        layer_id = db.Column(db.String(32), db.ForeignKey('layers.id'), nullable=False)
        version_number = db.Column(db.Integer, nullable=False)
        version_name = db.Column(db.String(100))
        description = db.Column(db.Text)
        layer_config = db.Column(db.JSON, nullable=False)
        feature_count = db.Column(db.Integer, default=0)
        created_by = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        __table_args__ = (
            db.UniqueConstraint('layer_id', 'version_number'),
        )
        
        # Relacionamentos
        creator = db.relationship('User', backref='created_versions')

    # ================================================
    # EVENT LISTENERS
    # ================================================

    @event.listens_for(User, 'before_insert')
    def receive_before_insert_user(mapper, connection, target):
        """Trigger antes de inserir usuário"""
        if not target.id:
            target.id = os.urandom(16).hex()

    @event.listens_for(Feature, 'before_insert')
    @event.listens_for(Feature, 'before_update')
    def calculate_feature_metrics(mapper, connection, target):
        """Calcular métricas da feature automaticamente"""
        target.calculate_metrics()

else:
    # Fallback classes quando SQLAlchemy não está disponível
    class Organization:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class User:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Project:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Layer:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Feature:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class Gleba:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# ================================================
# INITIALIZATION FUNCTIONS
# ================================================

def init_enhanced_database():
    """Inicializar banco de dados com estrutura melhorada"""
    if not SQLALCHEMY_AVAILABLE:
        return False
    
    try:
        # Criar todas as tabelas
        db.create_all()
        
        # Criar organização padrão se não existir
        default_org = Organization.query.filter_by(slug='webag-default').first()
        if not default_org:
            default_org = Organization(
                name='WEBAG Professional',
                slug='webag-default',
                description='Organização padrão do sistema',
                subscription_plan='enterprise',
                max_users=100,
                max_projects=50,
                max_storage_mb=10000
            )
            db.session.add(default_org)
            db.session.commit()
        
        # Criar usuário administrador se não existir
        admin_user = User.query.filter_by(username='admin_super').first()
        if not admin_user:
            admin_user = User(
                organization_id=default_org.id,
                username='admin_super',
                email='admin@webag.com',
                first_name='Administrador',
                last_name='Sistema',
                role='superuser',
                privileges={
                    'canManageOrganization': True,
                    'canManageUsers': True,
                    'canManageProjects': True,
                    'canManageLayers': True,
                    'canEditLayers': True,
                    'canDeleteLayers': True,
                    'canExportData': True,
                    'canImportData': True,
                    'canViewAuditLog': True,
                    'canManageSystem': True
                }
            )
            admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'AdminPass123!'))
            db.session.add(admin_user)
            db.session.commit()
        
        # Criar projeto padrão se não existir
        default_project = Project.query.filter_by(slug='projeto-principal').first()
        if not default_project:
            default_project = Project(
                organization_id=default_org.id,
                name='Projeto Principal',
                slug='projeto-principal',
                description='Projeto principal do sistema WEBAG',
                project_type=ProjectType.TOPOGRAPHY,
                owner_id=admin_user.id
            )
            db.session.add(default_project)
            db.session.commit()
        
        return True
        
    except Exception as e:
        print(f"Erro inicializando banco de dados: {e}")
        return False

def get_db_stats() -> Dict[str, Any]:
    """Obter estatísticas do banco de dados"""
    if not SQLALCHEMY_AVAILABLE:
        return {}
    
    try:
        stats = {
            'organizations': Organization.query.count(),
            'users': User.query.count(),
            'projects': Project.query.count(),
            'layers': Layer.query.count(),
            'features': Feature.query.count(),
            'glebas': Gleba.query.count(),
            'audit_logs': AuditLog.query.count(),
        }
        return stats
    except:
        return {}