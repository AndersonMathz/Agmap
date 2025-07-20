#!/usr/bin/env python3
"""
WEBAG Simple - Versão simplificada para produção
"""

import os
from flask import Flask, render_template, jsonify

def create_simple_app():
    """Criar aplicação Flask simplificada"""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    app.config['DEBUG'] = False
    
    @app.route('/')
    def index():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WEBAG Professional</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .error { background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .info { background: #e8f0ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
                ul { line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 WEBAG Professional</h1>
                
                <div class="status">
                    <h3>✅ Sistema Online</h3>
                    <p>Aplicação Flask inicializada com sucesso no Render!</p>
                </div>
                
                <div class="info">
                    <h3>📊 Status do Sistema</h3>
                    <ul>
                        <li><strong>Ambiente:</strong> Produção (Render)</li>
                        <li><strong>Framework:</strong> Flask + Python</li>
                        <li><strong>Banco:</strong> PostgreSQL (configurado)</li>
                        <li><strong>Status:</strong> Funcionando</li>
                    </ul>
                </div>
                
                <h3>🔗 Links Úteis</h3>
                <ul>
                    <li><a href="/health">Health Check (API)</a></li>
                    <li><a href="/status">Status Detalhado</a></li>
                    <li><a href="/config">Configurações</a></li>
                </ul>
                
                <div class="info">
                    <h3>🛠️ Próximos Passos</h3>
                    <p>A aplicação está funcionando! Agora você pode:</p>
                    <ol>
                        <li>Verificar se o banco PostgreSQL está conectado</li>
                        <li>Fazer login com usuário administrador</li>
                        <li>Começar a usar o sistema WebGIS</li>
                    </ol>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "ok",
            "message": "WEBAG Professional está funcionando",
            "environment": "production",
            "database": "postgresql" if os.environ.get('DATABASE_URL') else "not_configured"
        })
    
    @app.route('/status')
    def status():
        return jsonify({
            "application": "WEBAG Professional",
            "status": "running",
            "version": "1.0.0",
            "environment": {
                "FLASK_ENV": os.environ.get('FLASK_ENV', 'not_set'),
                "DATABASE_URL": "configured" if os.environ.get('DATABASE_URL') else "missing",
                "SECRET_KEY": "configured" if os.environ.get('SECRET_KEY') else "missing"
            },
            "features": [
                "WebGIS Interface",
                "PostgreSQL Database", 
                "User Authentication",
                "File Upload",
                "Layer Management"
            ]
        })
    
    @app.route('/config')
    def config():
        safe_env = {}
        for key, value in os.environ.items():
            if 'SECRET' in key or 'PASSWORD' in key or 'KEY' in key:
                safe_env[key] = '***configured***'
            elif 'DATABASE_URL' in key:
                safe_env[key] = 'postgresql://***:***@***/**' if value else 'not_set'
            else:
                safe_env[key] = value
                
        return jsonify({
            "message": "Configurações do sistema (dados sensíveis ocultados)",
            "environment_variables": safe_env
        })
    
    return app

# Para uso direto
app = create_simple_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)