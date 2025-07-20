#!/usr/bin/env python3
"""
Servidor de teste simples para verificar conectividade
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Servidor funcionando!', 'status': 'ok'})

@app.route('/test-login', methods=['POST'])
def test_login():
    data = request.get_json()
    return jsonify({
        'message': 'Login recebido',
        'data': data,
        'success': True
    })

if __name__ == '__main__':
    print("🚀 Servidor de teste iniciado!")
    print("URL: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)