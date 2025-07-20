#!/usr/bin/env python3
"""
WSGI entry point para produção no Render
"""

import os
import sys
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar ambiente para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Verificar se DATABASE_URL está configurada
if not os.environ.get('DATABASE_URL'):
    logger.warning("DATABASE_URL não configurada, usando SQLite em memória")

try:
    # Tentar importar e criar app
    from app import create_app
    app = create_app('production')
    logger.info("✅ Aplicação criada com sucesso")
    
except ImportError as e:
    logger.error(f"❌ Erro de import: {e}")
    # Fallback mais simples
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def hello():
            return "WEBAG está inicializando... Verifique os logs."
            
        @app.route('/health')
        def health():
            return {"status": "ok", "message": "Aplicação rodando com fallback"}
            
        logger.info("⚠️ Usando aplicação de fallback")
    except Exception as e2:
        logger.error(f"❌ Erro crítico: {e2}")
        raise

except Exception as e:
    logger.error(f"❌ Erro na criação da aplicação: {e}")
    raise

# Configuração para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 