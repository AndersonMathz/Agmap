#!/usr/bin/env python3
"""
WSGI entry point para produção
"""

import os
from app import create_app

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'production')

# Criar aplicação
app = create_app('production')

if __name__ == '__main__':
    app.run() 