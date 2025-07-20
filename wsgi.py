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
    # Tentar aplicação principal garantida
    from main_app import app
    logger.info("✅ Aplicação principal (main_app.py) carregada com sucesso")
    
except Exception as e:
    logger.warning(f"⚠️ Aplicação completa falhou: {e}")
    try:
        # Tentar versão simplificada
        from app_simple import create_simple_app
        app = create_simple_app()
        logger.info("✅ Aplicação simplificada criada com sucesso")
    except Exception as e2:
        logger.warning(f"⚠️ Aplicação simplificada falhou: {e2}")
        try:
            # Tentar versão mínima (sem SQLAlchemy)
            from app_minimal import create_minimal_app
            app = create_minimal_app()
            logger.info("✅ Aplicação mínima criada com sucesso")
        except Exception as e3:
            logger.error(f"❌ Todas as versões falharam: {e} | {e2} | {e3}")
            raise Exception(f"Todas as versões falharam")
    
except ImportError as e:
    logger.error(f"❌ Erro de import: {e}")
    # Fallback mais informativo
    try:
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def hello():
            return f"""
            <h1>🚀 WEBAG Professional</h1>
            <p><strong>Status:</strong> Inicializando com fallback</p>
            <p><strong>Erro:</strong> {str(e)}</p>
            <p><strong>Solução:</strong> Verificando configurações...</p>
            <hr>
            <h3>Informações do Sistema:</h3>
            <ul>
                <li>DATABASE_URL: {'✅ Configurada' if os.environ.get('DATABASE_URL') else '❌ Não configurada'}</li>
                <li>SECRET_KEY: {'✅ Configurada' if os.environ.get('SECRET_KEY') else '❌ Não configurada'}</li>
                <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'Não definida')}</li>
            </ul>
            <p><a href="/health">Verificar Health Check</a></p>
            <p><a href="/debug">Informações de Debug</a></p>
            """
            
        @app.route('/health')
        def health():
            return jsonify({
                "status": "fallback", 
                "message": "Aplicação rodando com fallback",
                "error": str(e),
                "env_vars": {
                    "DATABASE_URL": "configured" if os.environ.get('DATABASE_URL') else "missing",
                    "SECRET_KEY": "configured" if os.environ.get('SECRET_KEY') else "missing",
                    "FLASK_ENV": os.environ.get('FLASK_ENV', "not_set")
                }
            })
            
        @app.route('/debug')
        def debug():
            import sys
            return jsonify({
                "python_version": sys.version,
                "path": sys.path[:5],  # Primeiros 5 paths
                "environment": dict(os.environ),
                "error": str(e)
            })
            
        logger.info("⚠️ Usando aplicação de fallback com debug")
    except Exception as e2:
        logger.error(f"❌ Erro crítico no fallback: {e2}")
        raise

except Exception as e:
    logger.error(f"❌ Erro na criação da aplicação: {e}")
    raise

# Configuração para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 