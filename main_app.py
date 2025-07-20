#!/usr/bin/env python3
"""
WEBAG Main App - Aplicação principal garantida para funcionar
"""

import os
import sys

# Garantir que o diretório atual está no path
sys.path.insert(0, os.path.dirname(__file__))

# Importar a função create_app do app.py principal
try:
    # Tentar importar create_app do app.py raiz
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_main", os.path.join(os.path.dirname(__file__), "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    # Criar a aplicação
    app = app_module.create_app('production')
    
    # CORREÇÃO CRÍTICA: Garantir inicialização do banco
    with app.app_context():
        try:
            # Tentar importar enhanced models primeiro
            from app.models.enhanced_models import init_enhanced_database, SQLALCHEMY_AVAILABLE
            if SQLALCHEMY_AVAILABLE:
                print("Inicializando banco enhanced...")
                init_enhanced_database()
                print("Banco enhanced inicializado!")
            else:
                # Fallback para banco simples
                from app.models.models import init_users, db
                if db:
                    db.create_all()
                    init_users()
                    print("Banco simples inicializado!")
        except Exception as e:
            print(f"Erro na inicializacao do banco: {e}")
            # Força criação das tabelas básicas
            try:
                if hasattr(app_module, 'db') and app_module.db:
                    app_module.db.create_all()
                    print("Tabelas basicas criadas!")
            except Exception as e2:
                print(f"Erro critico no banco: {e2}")
    
except Exception as e:
    print(f"Erro ao carregar app.py: {e}")
    # Fallback para app mínimo
    from flask import Flask, jsonify, request, redirect, url_for, session
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    
    # Usuários simples em memória para fallback
    USERS = {
        'admin_super': {'password': 'admin123', 'name': 'Administrador'},
        'admin': {'password': 'admin', 'name': 'Admin'}
    }
    
    @app.route('/')
    def index():
        if 'user' in session:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>WEBAG Professional</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }}
                    .card {{ background: rgba(255,255,255,0.9); color: #333; padding: 40px; border-radius: 15px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #2c3e50; }}
                    .btn {{ display: inline-block; background: #3498db; color: white; padding: 12px 24px; border-radius: 25px; text-decoration: none; margin: 10px; }}
                    .logout {{ background: #e74c3c; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🚀 WEBAG Professional</h1>
                    <p>Bem-vindo, {session['user']}!</p>
                    <p>
                        <a href="/webgis" class="btn">WebGIS</a>
                        <a href="/api/health" class="btn">Status</a>
                        <a href="/logout" class="btn logout">Sair</a>
                    </p>
                </div>
            </body>
            </html>
            """
        else:
            return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.get_json() or request.form
            username = data.get('username')
            password = data.get('password')
            
            if username in USERS and USERS[username]['password'] == password:
                session['user'] = USERS[username]['name']
                return jsonify({'success': True, 'redirect': '/'})
            else:
                return jsonify({'error': 'Credenciais inválidas'}), 401
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WEBAG Login</title>
            <style>
                body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
                .login-form { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); max-width: 400px; width: 100%; }
                input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                button { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <div class="login-form">
                <h2>🔐 WEBAG Login</h2>
                <form onsubmit="doLogin(event)">
                    <input type="text" id="username" placeholder="Usuário" value="admin_super" required>
                    <input type="password" id="password" placeholder="Senha" value="admin123" required>
                    <button type="submit">Entrar</button>
                </form>
                <div id="message"></div>
            </div>
            <script>
                function doLogin(e) {
                    e.preventDefault();
                    fetch('/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            username: document.getElementById('username').value,
                            password: document.getElementById('password').value
                        })
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = data.redirect;
                        } else {
                            document.getElementById('message').innerHTML = '<p style="color: red;">' + data.error + '</p>';
                        }
                    })
                    .catch(e => {
                        document.getElementById('message').innerHTML = '<p style="color: red;">Erro de conexão</p>';
                    });
                }
            </script>
        </body>
        </html>
        """
    
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('login'))
    
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "ok",
            "message": "WEBAG funcionando",
            "mode": "fallback",
            "user": session.get('user', 'Não logado')
        })
    
    @app.route('/webgis')
    def webgis():
        if 'user' not in session:
            return redirect(url_for('login'))
        return """
        <!DOCTYPE html>
        <html>
        <head><title>WEBAG WebGIS</title></head>
        <body style="font-family: Arial; padding: 40px;">
            <h1>🗺️ WEBAG WebGIS</h1>
            <p>Interface WebGIS em desenvolvimento...</p>
            <p><a href="/" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar</a></p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
