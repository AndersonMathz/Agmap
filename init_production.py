#!/usr/bin/env python3
"""
Script de inicialização para produção no Render
"""

import os
import sys
from app import create_app
from app.models.enhanced_models import init_enhanced_database

def init_production_database():
    """Inicializar banco de dados para produção"""
    print("🚀 Inicializando banco de dados para produção...")
    
    try:
        app = create_app('production')
        
        with app.app_context():
            # Tentar inicializar banco enhanced
            if init_enhanced_database():
                print("✅ Banco de dados enhanced inicializado com sucesso!")
            else:
                print("⚠️ Usando inicialização básica...")
                # Fallback para inicialização básica
                from app.models.models import init_users
                if hasattr(init_users, '__call__'):
                    init_users()
                    print("✅ Usuários inicializados!")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

if __name__ == '__main__':
    init_production_database()