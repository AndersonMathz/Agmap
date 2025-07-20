#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEBAG - Teste do Sistema Completo
Testa todas as funcionalidades implementadas ate agora
"""
import sys
import os
sys.path.append('.')

def test_database():
    """Testa conectividade e dados do banco"""
    print("=== TESTE DATABASE ===")
    try:
        import sqlite3
        db_path = "instance/webgis.db"
        
        if not os.path.exists(db_path):
            print("❌ Banco nao encontrado")
            return False
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Testar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['users', 'projects', 'geo_features', 'uploaded_files']
            missing = [t for t in expected_tables if t not in tables]
            
            if missing:
                print(f"❌ Tabelas faltando: {missing}")
                return False
            
            # Testar dados
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM geo_features")
            features_count = cursor.fetchone()[0]
            
            print(f"✅ Database OK: {len(tables)} tabelas, {users_count} usuarios, {features_count} features")
            return True
            
    except Exception as e:
        print(f"❌ Erro database: {e}")
        return False

def test_core_utils():
    """Testa utilitarios core"""
    print("=== TESTE CORE UTILS ===")
    try:
        from app.utils.core_utils import sanitize_user_input, allowed_file, validate_coordinates
        
        # Teste sanitizacao
        malicious = '<script>alert("xss")</script>admin'
        clean = sanitize_user_input(malicious)
        if '<script>' in clean:
            print("❌ Sanitizacao falhou")
            return False
        
        # Teste validacao arquivo
        if not allowed_file('test.kml'):
            print("❌ Validacao KML falhou")
            return False
        
        if allowed_file('virus.exe'):
            print("❌ Validacao EXE falhou")
            return False
        
        # Teste coordenadas
        valid, _ = validate_coordinates(-23.5505, -46.6333)
        if not valid:
            print("❌ Validacao coordenadas falhou")
            return False
        
        invalid, _ = validate_coordinates(200, 400)
        if invalid:
            print("❌ Rejeicao coordenadas falhou")
            return False
        
        print("✅ Core Utils OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro core utils: {e}")
        return False

def test_models():
    """Testa modelos (sem Flask)"""
    print("=== TESTE MODELS ===")
    try:
        from app.models.models import users_db, init_users, authenticate_user
        
        # Limpar e reinicializar
        users_db.clear()
        
        # Configurar senha via environment
        os.environ['ADMIN_PASSWORD'] = 'TestPass123'
        
        # Inicializar usuarios
        init_users()
        
        if 'admin_super' not in users_db:
            print("❌ Usuario admin nao criado")
            return False
        
        # Testar autenticacao
        user = authenticate_user('admin_super', 'TestPass123')
        if not user:
            print("❌ Autenticacao valida falhou")
            return False
        
        # Testar autenticacao invalida
        user_invalid = authenticate_user('admin_super', 'senha_errada')
        if user_invalid:
            print("❌ Autenticacao invalida passou")
            return False
        
        print("✅ Models OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro models: {e}")
        return False

def test_file_structure():
    """Testa estrutura de arquivos"""
    print("=== TESTE ESTRUTURA ===")
    
    required_dirs = [
        'app', 'app/models', 'app/utils', 'app/views', 'app/services',
        'config', 'static', 'templates', 'tests', 'docs', 'scripts'
    ]
    
    required_files = [
        'app.py', 'requirements.txt', 'docker-compose.yml',
        'app/__init__.py', 'app/models/__init__.py',
        'config/config.py', 'sql/init.sql', 'sql/sqlite_init.sql'
    ]
    
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_dirs:
        print(f"❌ Diretorios faltando: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Arquivos faltando: {missing_files}")
        return False
    
    print("✅ Estrutura OK")
    return True

def test_security():
    """Testa implementacoes de seguranca"""
    print("=== TESTE SEGURANCA ===")
    
    # Verificar se arquivos sensiveis foram removidos
    sensitive_files = ['api_claude.txt', 'api_key.txt', 'credentials.txt']
    found_sensitive = [f for f in sensitive_files if os.path.exists(f)]
    
    if found_sensitive:
        print(f"❌ Arquivos sensiveis encontrados: {found_sensitive}")
        return False
    
    # Verificar .gitignore
    if not os.path.exists('.gitignore'):
        print("❌ .gitignore nao encontrado")
        return False
    
    # Verificar .env.example
    if not os.path.exists('.env.example'):
        print("❌ .env.example nao encontrado")
        return False
    
    print("✅ Seguranca OK")
    return True

def main():
    """Funcao principal"""
    print("=" * 50)
    print("WEBAG PROFESSIONAL - TESTE COMPLETO DO SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("Seguranca", test_security),
        ("Database", test_database),
        ("Core Utils", test_core_utils),
        ("Models", test_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FALHOU")
        except Exception as e:
            print(f"❌ {test_name} ERRO: {e}")
    
    print("=" * 50)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        return 0
    else:
        print("⚠️  Sistema parcialmente funcional")
        return 1

if __name__ == "__main__":
    exit(main())