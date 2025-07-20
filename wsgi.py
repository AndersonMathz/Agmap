#!/usr/bin/env python3
"""
WSGI entry point para produção no Render
"""

import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar ambiente para produção
os.environ.setdefault('FLASK_ENV', 'production')

# Importar factory function
try:
    from app import create_app
    app = create_app('production')
except ImportError:
    # Fallback se houver problemas de import
    import app as app_module
    app = app_module.app

# Configuração para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 