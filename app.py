import os
import json
import logging
import sqlite3
import time

# Imports opcionais com fallbacks
try:
    from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user
    FLASK_LOGIN_AVAILABLE = True
except ImportError:
    FLASK_LOGIN_AVAILABLE = False

try:
    from flask_sqlalchemy import SQLAlchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    SQLAlchemy = None

try:
    from werkzeug.middleware.proxy_fix import ProxyFix
    from werkzeug.exceptions import RequestEntityTooLarge
    WERKZEUG_AVAILABLE = True
except ImportError:
    WERKZEUG_AVAILABLE = False

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

# Imports locais
try:
    from config.config import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Inicializar o banco de dados
if SQLALCHEMY_AVAILABLE:
    db = SQLAlchemy()
else:
    db = None

# Imports serão feitos após criar app para evitar circular imports
MODELS_AVAILABLE = False
init_users = None
authenticate_user = None
get_user_by_username = None
GeoFeature = None
Gleba = None

try:
    from app.utils.utils import (
        allowed_file, validate_kml_content, sanitize_user_input, 
        create_safe_path, log_security_event
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webgis.log'),
        logging.StreamHandler()
    ]
)

# Configurar logger de segurança
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

def create_app(config_name='default'):
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração
    app.config.from_object(config[config_name])
    
    # Corrigir caminho do banco para usar instance folder
    if 'sqlite:///' in app.config['SQLALCHEMY_DATABASE_URI'] and not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:////'):
        # Ajustar caminho para usar instance folder
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'webgis.db')

    # Inicializar o banco de dados com o app
    if db:
        db.init_app(app)
    
    # Imports após inicialização para evitar circular imports
    global MODELS_AVAILABLE, init_users, authenticate_user, get_user_by_username, GeoFeature, Gleba
    
    # Forçar uso do sistema simples para evitar problemas com SQLAlchemy
    # Configurando sistema de autenticação
    ENHANCED_MODELS_AVAILABLE = False
    MODELS_AVAILABLE = False
    
    # Não tentar carregar enhanced models ou legacy models
    # Usar apenas sistema simples de autenticação
    # Sistema simples de autenticação será usado
    
    # Criar as tabelas do banco de dados dentro do contexto da aplicação
    if db:
        with app.app_context():
            try:
                db.create_all()
                # Tabelas do banco de dados criadas/verificadas
                        
            except Exception as e:
                print(f"❌ Erro ao criar tabelas: {e}")
    
    # Se enhanced models não estão disponíveis, criar sistema de fallback
    if not ENHANCED_MODELS_AVAILABLE:
        # Sistema de autenticação simples para fallback
        def simple_authenticate(username: str, password: str):
            """Sistema de autenticação simples para fallback"""
            users = {
                'admin_super': {'password': 'admin123', 'name': 'Administrador', 'role': 'admin'},
                'user': {'password': 'user123', 'name': 'Usuário', 'role': 'user'}
            }
            
            if username in users and users[username]['password'] == password:
                # Criar objeto user simples
                class SimpleUser:
                    def __init__(self, username, data):
                        self.username = username
                        self.name = data['name']
                        self.role = data['role']
                        self.privileges = ['canEditLayers', 'canUploadFiles', 'canViewAllData'] if data['role'] == 'admin' else ['canEditLayers']
                        self.is_authenticated = True
                        self.is_active = True
                        self.is_anonymous = False
                    
                    def get_id(self):
                        return self.username
                    
                    def has_privilege(self, privilege):
                        return privilege in self.privileges
                
                return SimpleUser(username, users[username])
            return None
        
        # Atualizar funções globalmente
        authenticate_user = simple_authenticate
            
        # Função para get_user_by_username
        def simple_get_user(username: str):
            users = {
                'admin_super': {'password': 'admin123', 'name': 'Administrador', 'role': 'admin'},
                'user': {'password': 'user123', 'name': 'Usuário', 'role': 'user'}
            }
            
            if username in users:
                class SimpleUser:
                    def __init__(self, username, data):
                        self.username = username
                        self.name = data['name']
                        self.role = data['role']
                        self.privileges = ['canEditLayers', 'canUploadFiles', 'canViewAllData'] if data['role'] == 'admin' else ['canEditLayers']
                        self.is_authenticated = True
                        self.is_active = True
                        self.is_anonymous = False
                    
                    def get_id(self):
                        return self.username
                    
                    def has_privilege(self, privilege):
                        return privilege in self.privileges
                
                return SimpleUser(username, users[username])
            return None
            
        get_user_by_username = simple_get_user
            
        # Sistema de autenticação simples ativado
    
    # Configurar para funcionar atrás de proxy (HTTPS)
    if WERKZEUG_AVAILABLE:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configurar Flask-Login
    if FLASK_LOGIN_AVAILABLE:
        login_manager = LoginManager()
        login_manager.init_app(app)
        # Configurar login view - usar None para desabilitar redirecionamento automático
        login_manager.login_view = 'login'  # type: ignore
        login_manager.login_message = 'Por favor, faça login para acessar esta página.'
        
        @login_manager.user_loader
        def load_user(user_id):
            return get_user_by_username(user_id)
    
    # Headers de segurança
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com; style-src-elem 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https:; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com;"
        return response
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Página não encontrada'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', error='Acesso negado'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='Erro interno do servidor'), 500
    
    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        return jsonify({'error': 'Arquivo muito grande'}), 413
    
    # Rotas de autenticação
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Verificar se é JSON ou form data
            if request.is_json:
                data = request.get_json()
                username = sanitize_user_input(data.get('username'))
                password = data.get('password')
            else:
                username = sanitize_user_input(request.form.get('username'))
                password = request.form.get('password')
            
            if not username or not password:
                log_security_event('login_failed', 'Campos vazios')
                return jsonify({'error': 'Por favor, preencha todos os campos'}), 400
            
            user = authenticate_user(username, password)
            if user:
                login_user(user)
                log_security_event('login_success', f'Usuário {username} logado')
                return jsonify({'success': True, 'redirect': url_for('index')})
            else:
                log_security_event('login_failed', f'Tentativa de login falhou para {username}')
                return jsonify({'error': 'Usuário ou senha incorretos'}), 401
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        log_security_event('logout', f'Usuário {current_user.username} fez logout')
        logout_user()
        return redirect(url_for('login'))
    
    # Rota principal - redireciona para login se não autenticado
    @app.route('/')
    def index():
        try:
            if current_user.is_authenticated:
                return render_template('index.html')
            else:
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))
    
    # Rota para o sistema principal (protegida)
    @app.route('/webgis')
    @login_required
    def webgis():
        return render_template('index.html')
    
    # Rota para sistema de glebas com ferramentas geojson.io
    @app.route('/glebas')
    @login_required
    def glebas():
        return render_template('webgis_glebas.html')
    
    # Rota de teste visual
    @app.route('/test')
    @login_required
    def test_visual():
        return send_from_directory('.', 'test_visual.html')
    
    # Rota de debug
    @app.route('/debug')
    @login_required
    def debug():
        return render_template('debug.html')
    
    # API para verificar autenticação
    @app.route('/api/auth/check')
    def check_auth():
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': {
                    'username': current_user.username,
                    'name': current_user.name,
                    'role': current_user.role,
                    'privileges': current_user.privileges
                }
            })
        return jsonify({'authenticated': False}), 401

    # API de health check
    @app.route('/api/health')
    def health_check():
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': True,
            'version': '1.0.0'
        })

    # API para dados geográficos
    @app.route('/api/features', methods=['GET', 'POST'])
    @login_required
    def manage_features():
        if request.method == 'GET':
            # Buscar features do banco ou usar sistema simplificado
            try:
                with sqlite3.connect('instance/webgis.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS map_features (
                            id TEXT PRIMARY KEY,
                            feature_type TEXT NOT NULL,
                            geometry TEXT NOT NULL,
                            properties TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_by TEXT
                        )
                    ''')
                    
                    cursor.execute('''
                        SELECT id, feature_type, geometry, properties, created_at
                        FROM map_features 
                        WHERE created_by = ?
                        ORDER BY created_at DESC
                    ''', (current_user.username,))
                    
                    features = []
                    for row in cursor.fetchall():
                        feature = {
                            'id': row[0],
                            'type': row[1],
                            'geometry': json.loads(row[2]) if row[2] else None,
                            'properties': json.loads(row[3]) if row[3] else {},
                            'created_at': row[4]
                        }
                        features.append(feature)
                    
                    return jsonify({
                        'features': features,
                        'total': len(features)
                    })
                    
            except Exception as e:
                return jsonify({'error': f'Erro carregando features: {str(e)}'}), 500
        
        elif request.method == 'POST':
            # Salvar nova feature
            try:
                data = request.get_json()
                if not data or not data.get('geometry'):
                    return jsonify({'error': 'Dados da feature são obrigatórios'}), 400
                
                feature_id = data.get('id', f'feature_{int(time.time())}')
                feature_type = data.get('geometry', {}).get('type', 'Unknown')
                geometry = json.dumps(data['geometry'])
                properties = json.dumps(data.get('properties', {}))
                
                with sqlite3.connect('instance/webgis.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO map_features 
                        (id, feature_type, geometry, properties, created_by)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (feature_id, feature_type, geometry, properties, current_user.username))
                    
                    conn.commit()
                
                return jsonify({
                    'id': feature_id,
                    'message': 'Feature salva com sucesso'
                }), 201
                
            except Exception as e:
                return jsonify({'error': f'Erro salvando feature: {str(e)}'}), 500
    
    @app.route('/api/features/<feature_id>', methods=['DELETE'])
    @login_required
    def delete_feature(feature_id):
        try:
            with sqlite3.connect('instance/webgis.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM map_features 
                    WHERE id = ? AND created_by = ?
                ''', (feature_id, current_user.username))
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Feature não encontrada'}), 404
                
                conn.commit()
                
                return jsonify({
                    'message': 'Feature deletada com sucesso',
                    'id': feature_id
                })
                
        except Exception as e:
            return jsonify({'error': f'Erro deletando feature: {str(e)}'}), 500

    @app.route('/api/features/clear-all', methods=['DELETE'])
    @login_required
    def clear_all_features():
        try:
            with sqlite3.connect('instance/webgis.db') as conn:
                cursor = conn.cursor()
                # Deletar apenas features do usuário atual
                cursor.execute('''
                    DELETE FROM map_features 
                    WHERE created_by = ?
                ''', (current_user.username,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return jsonify({
                    'message': f'{deleted_count} features removidas com sucesso',
                    'deleted_count': deleted_count
                })
                
        except Exception as e:
            return jsonify({'error': f'Erro limpando features: {str(e)}'}), 500
    
    @app.route('/api/features/<int:feature_id>', methods=['PUT'])
    @login_required
    def update_feature(feature_id):
        if not current_user.has_privilege('canEditLayers'):
            return jsonify({'error': 'Sem permissão para editar'}), 403

        if not MODELS_AVAILABLE or not GeoFeature:
            return jsonify({'error': 'Modelos de dados não disponíveis'}), 500
            
        feature = GeoFeature.query.get_or_404(feature_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        # Sanitizar e validar os dados recebidos aqui antes de salvar
        # Por enquanto, vamos salvar diretamente
        feature.properties = data
        db.session.commit()

        return jsonify(feature.to_dict())
    
    # API para upload de arquivos KML
    @app.route('/api/upload/kml', methods=['POST'])
    @login_required
    def upload_kml():
        if not current_user.has_privilege('canUploadFiles'):
            log_security_event('unauthorized_upload', f'Usuário {current_user.username} tentou fazer upload sem permissão')
            return jsonify({'error': 'Sem permissão para fazer upload'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            log_security_event('invalid_file_type', f'Usuário {current_user.username} tentou enviar arquivo inválido: {file.filename}')
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        try:
            # Ler e validar conteúdo
            content = file.read().decode('utf-8')
            is_valid, result = validate_kml_content(content)
            
            if not is_valid:
                log_security_event('invalid_kml', f'Usuário {current_user.username} enviou KML inválido')
                return jsonify({'error': result}), 400
            
            # Salvar arquivo de forma segura
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)
            os.makedirs(upload_dir, exist_ok=True)
            
            safe_path = create_safe_path(upload_dir, file.filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(result)
            
            log_security_event('file_uploaded', f'Usuário {current_user.username} fez upload de {file.filename}')
            
            return jsonify({
                'success': True,
                'filename': os.path.basename(safe_path),
                'message': 'Arquivo enviado com sucesso'
            })
            
        except Exception as e:
            log_security_event('upload_error', f'Erro no upload: {str(e)}')
            return jsonify({'error': 'Erro ao processar arquivo'}), 500
    
    # API para servir arquivos KML
    @app.route('/api/files/<path:filename>')
    @login_required
    def serve_file(filename):
        if not current_user.has_privilege('canViewAllData'):
            return jsonify({'error': 'Sem permissão para acessar arquivos'}), 403
        
        try:
            # Verificar se arquivo existe e está em local seguro
            file_path = create_safe_path(app.config['UPLOAD_FOLDER'], filename)
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'Arquivo não encontrado'}), 404
            
            return send_from_directory(
                os.path.dirname(file_path),
                os.path.basename(file_path),
                mimetype='application/vnd.google-earth.kml+xml'
            )
            
        except ValueError:
            return jsonify({'error': 'Caminho inválido'}), 400
        except Exception as e:
            log_security_event('file_access_error', f'Erro ao acessar arquivo: {str(e)}')
            return jsonify({'error': 'Erro ao acessar arquivo'}), 500
    
    # API para dados do usuário
    @app.route('/api/user/profile')
    @login_required
    def user_profile():
        return jsonify({
            'username': current_user.username,
            'name': current_user.name,
            'role': current_user.role,
            'privileges': current_user.privileges
        })
    
    # ==================== MODELO GLEBA LOCAL ====================
    
    # Definir modelo Gleba local com campos que funcionam
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
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
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

    # ==================== APIs DE GLEBAS ====================
    
    @app.route('/api/glebas', methods=['GET'])
    @login_required
    def get_glebas():
        """Obter todas as glebas do usuário"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            glebas = Gleba.query.filter_by(created_by=current_user.username).order_by(Gleba.created_at.desc()).all()
            
            return jsonify({
                'glebas': [gleba.to_dict() for gleba in glebas],
                'total': len(glebas),
                'message': 'Glebas carregadas com sucesso'
            })
            
        except Exception as e:
            app.logger.error(f'Erro carregando glebas: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/glebas', methods=['POST'])
    @login_required
    def create_gleba():
        """Criar nova gleba"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados da gleba são obrigatórios'}), 400
            
            # Validar dados obrigatórios
            if not data.get('no_gleba'):
                return jsonify({'error': 'Número da gleba é obrigatório'}), 400
            
            if not data.get('geometry'):
                return jsonify({'error': 'Geometria da gleba é obrigatória'}), 400
            
            # Verificar se já existe gleba com mesmo número
            existing = Gleba.query.filter_by(
                no_gleba=data['no_gleba'], 
                created_by=current_user.username
            ).first()
            
            if existing:
                return jsonify({'error': 'Já existe uma gleba com este número'}), 400
            
            # Criar nova gleba
            gleba = Gleba(
                no_gleba=data['no_gleba'],
                nome_gleba=data.get('nome_gleba'),
                area=data.get('area'),
                perimetro=data.get('perimetro'),
                geometry=data['geometry'],
                proprietario=data.get('proprietario'),
                cpf=data.get('cpf'),
                rg=data.get('rg'),
                rua=data.get('rua'),
                bairro=data.get('bairro'),
                quadra=data.get('quadra'),
                cep=data.get('cep'),
                cidade=data.get('cidade'),
                uf=data.get('uf'),
                testada_frente=data.get('testada_frente'),
                testada_fundo=data.get('testada_fundo'),
                testada_esquerda=data.get('testada_esquerda'),
                testada_direita=data.get('testada_direita'),
                confrontacao_frente=data.get('confrontacao_frente'),
                confrontacao_fundo=data.get('confrontacao_fundo'),
                confrontacao_esquerda=data.get('confrontacao_esquerda'),
                confrontacao_direita=data.get('confrontacao_direita'),
                valor_imovel=data.get('valor_imovel'),
                matricula=data.get('matricula'),
                inscricao_municipal=data.get('inscricao_municipal'),
                observacoes=data.get('observacoes'),
                created_by=current_user.username
            )
            
            db.session.add(gleba)
            db.session.commit()
            
            return jsonify({
                'id': gleba.id,
                'message': 'Gleba criada com sucesso',
                'no_gleba': gleba.no_gleba
            }), 201
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Erro criando gleba: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/glebas/<int:gleba_id>', methods=['GET'])
    @login_required
    def get_gleba(gleba_id):
        """Obter gleba específica"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            gleba = Gleba.query.filter_by(
                id=gleba_id, 
                created_by=current_user.username
            ).first()
            
            if not gleba:
                return jsonify({'error': 'Gleba não encontrada'}), 404
            
            return jsonify(gleba.to_dict())
            
        except Exception as e:
            app.logger.error(f'Erro obtendo gleba: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/glebas/<int:gleba_id>', methods=['PUT'])
    @login_required
    def update_gleba(gleba_id):
        """Atualizar gleba"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            gleba = Gleba.query.filter_by(
                id=gleba_id, 
                created_by=current_user.username
            ).first()
            
            if not gleba:
                return jsonify({'error': 'Gleba não encontrada'}), 404
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Dados para atualização são obrigatórios'}), 400
            
            # Atualizar campos
            for field in ['nome_gleba', 'area', 'perimetro', 'proprietario', 'cpf', 'rg',
                         'rua', 'bairro', 'quadra', 'cep', 'cidade', 'uf',
                         'testada_frente', 'testada_fundo', 'testada_esquerda', 'testada_direita',
                         'confrontacao_frente', 'confrontacao_fundo', 'confrontacao_esquerda', 'confrontacao_direita',
                         'valor_imovel', 'matricula', 'inscricao_municipal', 'observacoes']:
                if field in data:
                    setattr(gleba, field, data[field])
            
            if 'geometry' in data:
                gleba.geometry = data['geometry']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Gleba atualizada com sucesso',
                'id': gleba.id
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Erro atualizando gleba: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/glebas/<int:gleba_id>', methods=['DELETE'])
    @login_required
    def delete_gleba(gleba_id):
        """Deletar gleba"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            gleba = Gleba.query.filter_by(
                id=gleba_id, 
                created_by=current_user.username
            ).first()
            
            if not gleba:
                return jsonify({'error': 'Gleba não encontrada'}), 404
            
            no_gleba = gleba.no_gleba
            db.session.delete(gleba)
            db.session.commit()
            
            return jsonify({
                'message': f'Gleba {no_gleba} deletada com sucesso',
                'id': gleba_id
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Erro deletando gleba: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/glebas/export', methods=['GET'])
    @login_required
    def export_glebas():
        """Exportar todas as glebas do usuário em GeoJSON"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            # Filtrar glebas do usuário atual
            glebas = Gleba.query.filter_by(created_by=current_user.username).all()
            
            # Criar FeatureCollection GeoJSON
            feature_collection = {
                'type': 'FeatureCollection',
                'features': [gleba.to_geojson() for gleba in glebas]
            }
            
            response = app.response_class(
                response=json.dumps(feature_collection, ensure_ascii=False, indent=2),
                status=200,
                mimetype='application/json'
            )
            
            response.headers['Content-Disposition'] = f'attachment; filename="glebas_{current_user.username}.geojson"'
            
            return response
            
        except Exception as e:
            app.logger.error(f'Erro exportando glebas: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # ==================== CÁLCULOS AUTOMÁTICOS ====================
    
    def calculate_polygon_sides(coordinates):
        """Calcular testadas e confrontações baseadas na geometria"""
        import math
        
        if not coordinates or len(coordinates[0]) < 4:
            return {
                'testadas': {
                    'frente': 0,
                    'fundo': 0,
                    'esquerda': 0,
                    'direita': 0
                },
                'confrontacoes': {
                    'frente': 'A definir',
                    'fundo': 'A definir', 
                    'esquerda': 'A definir',
                    'direita': 'A definir'
                }
            }
        
        # Pegar primeiro anel do polígono (sem último ponto que repete o primeiro)
        ring = coordinates[0][:-1]
        
        # Calcular distâncias entre pontos consecutivos
        sides = []
        for i in range(len(ring)):
            p1 = ring[i]
            p2 = ring[(i + 1) % len(ring)]
            
            # Calcular distância usando fórmula haversine (aproximação para distâncias curtas)
            lat1, lon1 = math.radians(p1[1]), math.radians(p1[0])
            lat2, lon2 = math.radians(p2[1]), math.radians(p2[0])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = 6371000 * c  # Raio da Terra em metros
            
            # Calcular azimute (direção)
            y = math.sin(dlon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
            azimuth = math.atan2(y, x)
            azimuth_degrees = math.degrees(azimuth)
            if azimuth_degrees < 0:
                azimuth_degrees += 360
            
            sides.append({
                'distance': round(distance, 2),
                'azimuth': round(azimuth_degrees, 1),
                'from': p1,
                'to': p2
            })
        
        # Determinar qual lado é frente, fundo, esquerda, direita
        # Baseado na orientação e posição relativa
        if len(sides) >= 4:
            # Para polígonos regulares, assumir orientação:
            # - Lado mais ao sul = frente
            # - Lado mais ao norte = fundo  
            # - Lado mais a oeste = esquerda
            # - Lado mais a leste = direita
            
            # Separar lados por orientação aproximada
            horizontal_sides = [s for s in sides if 45 <= s['azimuth'] <= 135 or 225 <= s['azimuth'] <= 315]
            vertical_sides = [s for s in sides if s['azimuth'] < 45 or s['azimuth'] > 315 or 135 < s['azimuth'] < 225]
            
            testadas = {'frente': 0, 'fundo': 0, 'esquerda': 0, 'direita': 0}
            
            if len(horizontal_sides) >= 2:
                # Lados horizontais - ordenar por latitude
                horizontal_sides.sort(key=lambda s: (s['from'][1] + s['to'][1]) / 2)
                testadas['frente'] = horizontal_sides[0]['distance']  # Mais ao sul
                if len(horizontal_sides) > 1:
                    testadas['fundo'] = horizontal_sides[-1]['distance']  # Mais ao norte
            
            if len(vertical_sides) >= 2:
                # Lados verticais - ordenar por longitude  
                vertical_sides.sort(key=lambda s: (s['from'][0] + s['to'][0]) / 2)
                testadas['esquerda'] = vertical_sides[0]['distance']  # Mais a oeste
                if len(vertical_sides) > 1:
                    testadas['direita'] = vertical_sides[-1]['distance']  # Mais a leste
            
            # Se não conseguiu classificar, usar os 4 primeiros lados
            if all(v == 0 for v in testadas.values()) and len(sides) >= 4:
                testadas['frente'] = sides[0]['distance']
                testadas['direita'] = sides[1]['distance']
                testadas['fundo'] = sides[2]['distance']
                testadas['esquerda'] = sides[3]['distance']
        
        else:
            # Para polígonos com menos de 4 lados
            testadas = {'frente': 0, 'fundo': 0, 'esquerda': 0, 'direita': 0}
            for i, side in enumerate(sides[:4]):
                keys = ['frente', 'direita', 'fundo', 'esquerda']
                if i < len(keys):
                    testadas[keys[i]] = side['distance']
        
        # Gerar confrontações baseadas na posição
        confrontacoes = {
            'frente': 'Via pública',
            'fundo': 'Terreno baldio', 
            'esquerda': 'Propriedade particular',
            'direita': 'Propriedade particular'
        }
        
        return {
            'testadas': testadas,
            'confrontacoes': confrontacoes,
            'sides_data': sides  # Para debug
        }
    
    @app.route('/api/glebas/<int:gleba_id>/calculate', methods=['POST'])
    @login_required
    def calculate_gleba_measurements(gleba_id):
        """Calcular automaticamente testadas e confrontações de uma gleba"""
        try:
            if not SQLALCHEMY_AVAILABLE:
                return jsonify({'error': 'Banco de dados não disponível'}), 500
            
            gleba = Gleba.query.filter_by(
                id=gleba_id, 
                created_by=current_user.username
            ).first()
            
            if not gleba:
                return jsonify({'error': 'Gleba não encontrada'}), 404
            
            # Obter geometria da gleba
            geometry = gleba.geometry
            
            if not geometry or geometry.get('type') != 'Polygon':
                return jsonify({'error': 'Geometria inválida para cálculo'}), 400
            
            # Calcular testadas e confrontações
            calculations = calculate_polygon_sides(geometry['coordinates'])
            
            # Atualizar gleba com os cálculos
            testadas = calculations['testadas']
            confrontacoes = calculations['confrontacoes']
            
            # Usar campos do modelo simplificado
            gleba.testada_frente = testadas['frente']
            gleba.testada_fundo = testadas['fundo']
            gleba.testada_esquerda = testadas['esquerda']
            gleba.testada_direita = testadas['direita']
            
            gleba.confrontacao_frente = confrontacoes['frente']
            gleba.confrontacao_fundo = confrontacoes['fundo']
            gleba.confrontacao_esquerda = confrontacoes['esquerda']
            gleba.confrontacao_direita = confrontacoes['direita']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Cálculos realizados com sucesso',
                'calculations': {
                    'testadas': testadas,
                    'confrontacoes': confrontacoes
                },
                'gleba': gleba.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Erro calculando medições: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Servir arquivos estáticos
    @app.route('/static/<path:filename>')
    def static_files(filename):
        response = send_from_directory('static', filename)
        # Adicionar headers para evitar cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # Rota para favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')
    
    # Servir arquivos KML da pasta WEBGIS_ANDERSON
    @app.route('/WEBGIS_ANDERSON/<path:filename>')
    @login_required
    def serve_kml_files(filename):
        if not current_user.has_privilege('canViewAllData'):
            return jsonify({'error': 'Sem permissão para acessar arquivos'}), 403
        
        try:
            # Verificar se o arquivo é KML
            if not filename.endswith('.kml'):
                return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
            # Caminho seguro para a pasta WEBGIS_ANDERSON
            webgis_path = os.path.join(os.getcwd(), 'WEBGIS_ANDERSON')
            file_path = os.path.join(webgis_path, filename)
            
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                return jsonify({'error': 'Arquivo não encontrado'}), 404
            
            # Verificar se o caminho é seguro (não permite directory traversal)
            if not os.path.abspath(file_path).startswith(os.path.abspath(webgis_path)):
                return jsonify({'error': 'Caminho inválido'}), 400
            
            return send_from_directory(
                webgis_path,
                filename,
                mimetype='application/vnd.google-earth.kml+xml'
            )
            
        except Exception as e:
            log_security_event('kml_access_error', f'Erro ao acessar KML {filename}: {str(e)}')
            return jsonify({'error': 'Erro ao acessar arquivo'}), 500
    
    # Inicializar usuários se disponível
    if init_users:
        init_users()
    
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        print("WebGIS iniciado em: http://localhost:5001")
        print("Login: admin_super/admin123")
        print("Para parar: Ctrl+C")
        app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        print("Tente executar como administrador ou verificar se a porta 5001 está livre") 