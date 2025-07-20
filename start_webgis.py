#!/usr/bin/env python3
"""
WebGIS Starter - Inicializador limpo do sistema WebGIS
"""

import os
import sys

def start_webgis():
    """Inicia o WebGIS com configurações limpas"""
    
    print("🚀 Iniciando WebGIS...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app.py'):
        print("❌ Erro: Execute este script no diretório do WebGIS")
        sys.exit(1)
    
    # Importar e configurar
    try:
        from app import create_app
        
        # Criar aplicação
        app = create_app()
        
        # Configurações limpas
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        print("✅ WebGIS iniciado com sucesso!")
        print("🌐 Acesse: http://localhost:5001")
        print("👤 Login: admin_super / admin123")
        print("🛑 Para parar: Ctrl+C")
        print("-" * 40)
        
        # Iniciar servidor
        app.run(
            host='127.0.0.1',
            port=5001,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Instale as dependências: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_webgis()