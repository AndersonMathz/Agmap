#!/usr/bin/env python3
"""
Script para testar se o aplicativo WebGIS está funcionando corretamente
"""

def test_imports():
    """Testar se todos os imports estão funcionando"""
    print("🔍 Testando imports...")
    
    try:
        from app import create_app
        print("✅ app.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar app.py: {e}")
        return False
    
    try:
        from config import config
        print("✅ config.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar config.py: {e}")
        return False
    
    try:
        from models import User, init_users, authenticate_user
        print("✅ models.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar models.py: {e}")
        return False
    
    try:
        from utils import sanitize_filename, allowed_file, sanitize_html
        print("✅ utils.py importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar utils.py: {e}")
        return False
    
    return True

def test_flask_app():
    """Testar se o aplicativo Flask pode ser criado"""
    print("\n🔍 Testando criação do Flask app...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar Flask app: {e}")
        return False

def test_authentication():
    """Testar sistema de autenticação"""
    print("\n🔍 Testando sistema de autenticação...")
    
    try:
        from models import init_users, authenticate_user
        
        # Inicializar usuários
        init_users()
        print("✅ Usuários inicializados")
        
        # Testar autenticação
        user = authenticate_user('admin_super', 'isis/2020')
        if user and user.username == 'admin_super':
            print("✅ Autenticação funcionando")
            return True
        else:
            print("❌ Falha na autenticação")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema de autenticação: {e}")
        return False

def test_utils():
    """Testar funções utilitárias"""
    print("\n🔍 Testando funções utilitárias...")
    
    try:
        from utils import sanitize_filename, allowed_file, sanitize_html
        
        # Testar sanitização de filename
        safe_name = sanitize_filename("test<script>.kml")
        if '<script>' not in safe_name:
            print("✅ Sanitização de filename funcionando")
        else:
            print("❌ Falha na sanitização de filename")
            return False
        
        # Testar validação de arquivo
        if allowed_file("test.kml"):
            print("✅ Validação de arquivo funcionando")
        else:
            print("❌ Falha na validação de arquivo")
            return False
        
        # Testar sanitização HTML
        clean_html = sanitize_html("<script>alert('xss')</script><p>texto</p>")
        if '<script>' not in clean_html:
            print("✅ Sanitização HTML funcionando")
        else:
            print("❌ Falha na sanitização HTML")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas funções utilitárias: {e}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 Iniciando testes do WebGIS...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_flask_app,
        test_authentication,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado dos testes:")
    print(f"✅ Passaram: {passed}/{total}")
    print(f"❌ Falharam: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O WebGIS está funcionando corretamente.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    main() 