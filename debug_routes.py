#!/usr/bin/env python3
"""
Script para debug de rotas da aplicação
"""

import os
import sys

def debug_routes():
    """Debug das rotas da aplicação"""
    
    print("=== DEBUG ROTAS WEBAG ===")
    
    try:
        sys.path.insert(0, '.')
        os.environ['FLASK_ENV'] = 'production'
        
        print("Importando create_app...")
        # Redirecionar stdout para capturar prints
        from io import StringIO
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        from app import create_app
        app = create_app('default')  # Usar 'default' como no app.py
        
        # Restaurar stdout e mostrar saída capturada
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        print("Import bem-sucedido, criando app...")
        print("Saída capturada do create_app:")
        print(output)
        print("App criado com sucesso!")
        
        print(f"\nTotal de rotas: {len(app.url_map._rules)}")
        print("\nListando todas as rotas:")
        
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {rule.rule:<30} [{methods}] -> {rule.endpoint}")
        
        # Verificar se as functions específicas estão definidas
        print("\nVerificando functions específicas:")
        functions_to_check = [
            'manage_features', 'login', 'index', 'logout',
            'api_glebas', 'get_gleba', 'update_gleba'
        ]
        
        for func_name in functions_to_check:
            if hasattr(app, 'view_functions') and func_name in app.view_functions:
                print(f"  OK - {func_name}")
            else:
                print(f"  FAIL - {func_name}")
        
        # Tentar acessar alguns endpoints diretamente
        print("\nTestando endpoints:")
        with app.test_client() as client:
            endpoints = ['/', '/api/health', '/api/features', '/login']
            for endpoint in endpoints:
                try:
                    response = client.get(endpoint)
                    print(f"  {endpoint:<20} -> {response.status_code}")
                except Exception as e:
                    print(f"  {endpoint:<20} -> ERROR: {e}")
                    
        return True
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_routes()