#!/usr/bin/env python3
"""
Script para testar o carregamento da aplicação e identificar problemas
"""

import os
import sys

def test_app_loading():
    """Teste de carregamento da aplicação"""
    
    print("=== TESTE DE CARREGAMENTO DA APLICAÇÃO ===")
    
    # Verificar se podemos importar o módulo principal
    try:
        sys.path.insert(0, '.')
        print("1. Tentando importar app...")
        
        # Simular as variáveis de ambiente de produção
        os.environ['FLASK_ENV'] = 'production'
        
        # Tentar importar a função create_app
        from app import create_app
        print("   OK - Import de create_app bem-sucedido")
        
        # Tentar criar a aplicação
        print("2. Tentando criar aplicação...")
        app = create_app('production')
        print(f"   OK - Aplicacao criada: {app}")
        
        # Verificar rotas disponíveis
        print("3. Verificando rotas...")
        with app.app_context():
            rules = list(app.url_map.iter_rules())
            print(f"   OK - Total de rotas: {len(rules)}")
            
            # Listar algumas rotas importantes
            important_routes = ['/api/features', '/api/glebas', '/glebas', '/']
            for route in important_routes:
                found = any(str(rule) == route for rule in rules)
                status = "OK" if found else "FAIL"
                print(f"   {status} - {route}")
        
        print("\n4. Teste de endpoint health...")
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"   Status: {response.status_code}")
            print(f"   Data: {response.get_json()}")
        
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_loading()
    sys.exit(0 if success else 1)