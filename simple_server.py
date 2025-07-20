#!/usr/bin/env python3
"""
WebGIS Simple Server - Servidor simplificado para debug
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os

def create_simple_app():
    """Cria uma aplicação Flask simplificada"""
    
    app = Flask(__name__)
    app.secret_key = 'webgis-simple-key-2025'
    
    # Usuários simples
    USERS = {
        'admin_super': 'admin123',
        'user': 'user123'
    }
    
    @app.route('/')
    def index():
        if 'user' not in session:
            return redirect(url_for('login'))
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username in USERS and USERS[username] == password:
                session['user'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Credenciais inválidas')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('login'))
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'WebGIS Simple Server'})
    
    return app

if __name__ == '__main__':
    print("🚀 WebGIS Simple Server")
    print("🌐 http://localhost:5001")
    print("👤 admin_super / admin123")
    print("🛑 Ctrl+C para parar")
    
    app = create_simple_app()
    app.run(host='127.0.0.1', port=5001, debug=True)