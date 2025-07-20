#!/usr/bin/env python3
"""
WebGIS Application - Versão Corrigida
Sistema de Informações Geográficas Web
"""

import os
import sys
import json
import logging
from datetime import datetime

# Imports principais do Flask
from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for

def create_app():
    """Factory function para criar a aplicação Flask"""
    
    # Configurar logging para produção
    logging.basicConfig(level=logging.WARNING)
    
    # Criar aplicação Flask
    app = Flask(__name__)
    
    # Configurações de segurança
    app.config['SECRET_KEY'] = 'webgis-production-key-2025'
    app.config['SESSION_COOKIE_SECURE'] = False  # True em produção com HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
    
    # Sistema de autenticação simples
    USERS = {
        'admin_super': 'admin123',
        'user': 'user123'
    }
    
    def is_authenticated():
        """Verifica se o usuário está autenticado"""
        return 'user' in session and session['user'] in USERS
    
    def require_auth(f):
        """Decorator para rotas que requerem autenticação"""
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ===== ROTAS =====
    
    @app.route('/')
    def index():
        """Rota principal - redireciona para login se não autenticado"""
        if is_authenticated():
            return render_template('index.html')
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Rota de login"""
        if request.method == 'POST':
            # Verificar se é JSON ou form data
            if request.is_json:
                data = request.get_json()
                username = data.get('username', '').strip()
                password = data.get('password', '')
            else:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')
            
            # Validar credenciais
            if username in USERS and USERS[username] == password:
                session['user'] = username
                session['login_time'] = datetime.now().isoformat()
                
                # Resposta baseada no tipo de request
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login realizado com sucesso',
                        'redirect': url_for('index')
                    })
                else:
                    return redirect(url_for('index'))
            else:
                # Login falhou
                error_msg = 'Credenciais inválidas'
                if request.is_json:
                    return jsonify({'success': False, 'message': error_msg}), 401
                else:
                    return render_template('login.html', error=error_msg)
        
        # GET request - mostrar formulário de login
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Rota de logout"""
        session.clear()
        return redirect(url_for('login'))
    
    @app.route('/webgis')
    @require_auth
    def webgis():
        """Rota para o sistema WebGIS principal"""
        return render_template('index.html')
    
    @app.route('/glebas')
    @require_auth
    def glebas():
        """Rota para o sistema de glebas"""
        return render_template('webgis_glebas.html')
    
    # ===== API ENDPOINTS =====
    
    @app.route('/api/auth/check')
    def api_auth_check():
        """Verifica status de autenticação"""
        if is_authenticated():
            return jsonify({
                'authenticated': True,
                'user': session['user'],
                'role': 'admin' if session['user'] == 'admin_super' else 'user'
            })
        return jsonify({'authenticated': False}), 401
    
    @app.route('/api/health')
    def api_health():
        """Health check da API"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/features')
    @require_auth
    def api_features():
        """Lista de features (stub para compatibilidade)"""
        return jsonify({
            'type': 'FeatureCollection',
            'features': []
        })
    
    @app.route('/api/features', methods=['POST'])
    @require_auth
    def api_create_feature():
        """Criar nova feature (stub para compatibilidade)"""
        try:
            feature_data = request.get_json()
            # Aqui seria salvo no banco de dados
            return jsonify({
                'success': True,
                'id': 'temp_' + str(int(datetime.now().timestamp())),
                'message': 'Feature criada com sucesso'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # ===== ARQUIVOS ESTÁTICOS =====
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Servir arquivos estáticos"""
        try:
            response = send_from_directory('static', filename)
            # Headers para evitar cache durante desenvolvimento
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except Exception as e:
            return f"Erro ao carregar arquivo: {filename}", 404
    
    # ===== TRATAMENTO DE ERROS =====
    
    @app.errorhandler(404)
    def not_found(error):
        """Página não encontrada"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint não encontrado'}), 404
        return render_template('error.html', 
                             error_code=404, 
                             error_message='Página não encontrada'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Erro interno do servidor"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Erro interno do servidor'}), 500
        return render_template('error.html', 
                             error_code=500, 
                             error_message='Erro interno do servidor'), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        """Arquivo muito grande"""
        return jsonify({'error': 'Arquivo muito grande (máximo 50MB)'}), 413
    
    return app

def main():
    """Função principal"""
    try:
        # Verificar se estamos no diretório correto
        if not os.path.exists('templates'):
            print("❌ Erro: Execute no diretório do WebGIS (pasta templates não encontrada)")
            sys.exit(1)
        
        # Criar aplicação
        app = create_app()
        
        # Informações de inicialização
        print("🚀 WebGIS iniciado com sucesso!")
        print("🌐 Acesse: http://localhost:5001")
        print("👤 Login: admin_super / admin123")
        print("🛑 Para parar: Ctrl+C")
        print("-" * 50)
        
        # Iniciar servidor
        app.run(
            host='127.0.0.1',
            port=5001,
            debug=True,
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n✅ Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("🔧 Possíveis soluções:")
        print("  - Verifique se a porta 5001 está livre")
        print("  - Execute como administrador")
        print("  - Instale dependências: pip install flask")

if __name__ == '__main__':
    main()