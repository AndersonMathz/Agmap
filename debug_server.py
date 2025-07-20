#!/usr/bin/env python3
"""
WebGIS Debug Server - Diagnóstico e teste de funcionamento
"""

import sys
import os
import socket

def check_port(port):
    """Verifica se uma porta está livre"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # True se porta estiver livre
    except:
        return False

def diagnose_system():
    """Executa diagnósticos do sistema"""
    print("🔍 WebGIS - Diagnóstico do Sistema")
    print("=" * 40)
    
    # Verificar Python
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Verificar diretório atual
    print(f"📁 Diretório: {os.getcwd()}")
    
    # Verificar arquivos essenciais
    files_to_check = ['app.py', 'templates/index.html', 'static/styles.css']
    for file in files_to_check:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"{exists} {file}")
    
    # Verificar portas
    ports_to_check = [5001, 5000, 8000, 3000]
    print("\n🔌 Verificação de Portas:")
    for port in ports_to_check:
        status = "✅ Livre" if check_port(port) else "❌ Ocupada"
        print(f"  Porta {port}: {status}")
    
    # Verificar imports
    print("\n📦 Verificação de Dependências:")
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError:
        print("❌ Flask não instalado")
        return False
    
    try:
        import flask_login
        print("✅ Flask-Login disponível")
    except ImportError:
        print("⚠️ Flask-Login não disponível")
    
    try:
        import sqlite3
        print("✅ SQLite3 disponível")
    except ImportError:
        print("❌ SQLite3 não disponível")
    
    return True

def create_minimal_server():
    """Cria um servidor Flask mínimo para teste"""
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebGIS - Teste</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin: 50px; }
                .success { color: green; font-size: 24px; }
                .info { color: #666; margin: 20px; }
            </style>
        </head>
        <body>
            <h1 class="success">✅ WebGIS Flask Funcionando!</h1>
            <p class="info">Este é um teste mínimo do servidor Flask.</p>
            <p class="info">Se você está vendo esta página, o Flask está funcionando corretamente.</p>
            <hr>
            <p><strong>Próximos passos:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Pare este servidor (Ctrl+C)</li>
                <li>Execute: <code>python app.py</code></li>
                <li>Acesse: <a href="http://localhost:5001">http://localhost:5001</a></li>
            </ul>
        </body>
        </html>
        ''')
    
    @app.route('/test')
    def test():
        return {"status": "ok", "message": "Flask está funcionando", "port": 5001}
    
    return app

if __name__ == '__main__':
    # Executar diagnósticos
    if not diagnose_system():
        print("\n❌ Problemas encontrados nos diagnósticos")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🚀 Iniciando Servidor de Teste Mínimo")
    print("🌐 http://localhost:5001")
    print("🛑 Ctrl+C para parar")
    print("=" * 40)
    
    # Criar e executar servidor mínimo
    app = create_minimal_server()
    
    try:
        app.run(host='127.0.0.1', port=5001, debug=False)
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        print("🔧 Possíveis soluções:")
        print("  - Verifique se outra aplicação está usando a porta 5001")
        print("  - Execute como administrador")
        print("  - Tente uma porta diferente")