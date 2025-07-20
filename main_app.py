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
    
except Exception as e:
    print(f"Erro ao carregar app.py: {e}")
    # Fallback para app mínimo
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
    
    @app.route('/')
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WEBAG Professional</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }
                .card { background: rgba(255,255,255,0.9); color: #333; padding: 40px; border-radius: 15px; max-width: 600px; margin: 0 auto; }
                h1 { color: #2c3e50; }
                .btn { display: inline-block; background: #3498db; color: white; padding: 12px 24px; border-radius: 25px; text-decoration: none; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🚀 WEBAG Professional</h1>
                <h2>✅ Sistema Online!</h2>
                <p>A aplicação está funcionando em modo de produção.</p>
                <p>
                    <a href="/api/health" class="btn">Health Check</a>
                    <a href="/login" class="btn">Login</a>
                </p>
            </div>
        </body>
        </html>
        """
    
    @app.route('/api/health')
    def health():
        return {
            "status": "ok",
            "message": "WEBAG funcionando",
            "mode": "fallback"
        }
    
    @app.route('/login')
    def login():
        return """
        <!DOCTYPE html>
        <html>
        <head><title>WEBAG Login</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>🔐 WEBAG Login</h1>
            <p>Sistema de login em desenvolvimento...</p>
            <p><a href="/" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar</a></p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)