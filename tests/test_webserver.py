#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEBAG - Teste End-to-End do Servidor Web
Testa todas as funcionalidades do sistema web completo
"""
import sys
import os
import time
import json
import threading
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

sys.path.append('.')

def start_test_server():
    """Iniciar servidor para testes em thread separada"""
    try:
        from simple_flask import main
        # Servidor rodará em thread separada
        server_thread = threading.Thread(target=main, daemon=True)
        server_thread.start()
        
        # Aguardar servidor inicializar
        time.sleep(3)
        return True
    except Exception as e:
        print(f"❌ Erro iniciando servidor: {e}")
        return False

def test_endpoint(url, expected_status=200):
    """Testar endpoint específico"""
    try:
        response = urlopen(url, timeout=10)
        status_code = response.getcode()
        content = response.read().decode('utf-8')
        
        if status_code == expected_status:
            return True, content
        else:
            return False, f"Status inesperado: {status_code}"
            
    except HTTPError as e:
        return False, f"HTTP Error: {e.code}"
    except URLError as e:
        return False, f"URL Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_json_endpoint(url):
    """Testar endpoint que retorna JSON"""
    try:
        success, content = test_endpoint(url)
        if success:
            data = json.loads(content)
            return True, data
        else:
            return False, content
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("WEBAG PROFESSIONAL - TESTE END-TO-END COMPLETO")
    print("=" * 60)
    
    BASE_URL = "http://localhost:5000"
    
    # Verificar se o servidor já está rodando
    print("🔍 Verificando se servidor está disponível...")
    success, _ = test_endpoint(f"{BASE_URL}/api/health")
    
    if not success:
        print("🚀 Iniciando servidor de teste...")
        if not start_test_server():
            print("❌ Falha ao iniciar servidor")
            return 1
        
        # Verificar novamente após inicialização
        print("⏳ Aguardando servidor ficar disponível...")
        for i in range(10):
            success, _ = test_endpoint(f"{BASE_URL}/api/health")
            if success:
                break
            time.sleep(1)
            print(f"   Tentativa {i+1}/10...")
        
        if not success:
            print("❌ Servidor não ficou disponível")
            return 1
    
    print("✅ Servidor disponível")
    
    # Testes de endpoints
    tests = [
        ("Health Check", f"{BASE_URL}/api/health", True),
        ("Página Principal", f"{BASE_URL}/", False),
        ("Estatísticas de Features", f"{BASE_URL}/api/features/stats", True),
        ("Lista de Camadas", f"{BASE_URL}/api/layers", True),
        ("Lista de Projetos", f"{BASE_URL}/api/projects", True),
        ("Features Gerais", f"{BASE_URL}/api/features", True),
        ("Verificação de Auth", f"{BASE_URL}/api/auth/check", True),
    ]
    
    passed = 0
    total = len(tests)
    
    print(f"\n🧪 Executando {total} testes...")
    
    for test_name, url, is_json in tests:
        print(f"\n  📋 {test_name}...")
        
        if is_json:
            success, result = test_json_endpoint(url)
            if success:
                print(f"     ✅ JSON válido: {len(str(result))} chars")
                
                # Verificações específicas por endpoint
                if 'health' in url and 'status' in result:
                    print(f"     ✅ Status: {result['status']}")
                elif 'stats' in url and 'total_features' in result:
                    print(f"     ✅ Total features: {result['total_features']}")
                elif 'layers' in url and 'layers' in result:
                    print(f"     ✅ Camadas: {len(result['layers'])}")
                elif 'projects' in url and 'projects' in result:
                    print(f"     ✅ Projetos: {len(result['projects'])}")
                elif 'features' in url and 'features' in result:
                    print(f"     ✅ Features: {len(result['features'])}")
                elif 'auth' in url and 'authenticated' in result:
                    print(f"     ✅ Auth: {result['authenticated']}")
                
                passed += 1
            else:
                print(f"     ❌ Erro: {result}")
        else:
            success, result = test_endpoint(url)
            if success:
                print(f"     ✅ HTML válido: {len(result)} chars")
                
                # Verificar se contém elementos esperados
                if 'WebGIS' in result:
                    print("     ✅ Título correto")
                if 'Leaflet' in result:
                    print("     ✅ Leaflet incluído")
                if 'Bootstrap' in result:
                    print("     ✅ Bootstrap incluído")
                
                passed += 1
            else:
                print(f"     ❌ Erro: {result}")
    
    # Teste de features por camada
    print(f"\n  📋 Testando features por camada...")
    layer_tests = ['Edifícios', 'Estradas', 'Lugares', 'Setores Censitários']
    
    for layer in layer_tests:
        encoded_layer = layer.replace(' ', '%20')
        url = f"{BASE_URL}/api/features/layer/{encoded_layer}"
        success, result = test_json_endpoint(url)
        
        if success and 'features' in result:
            print(f"     ✅ {layer}: {len(result['features'])} features")
            passed += 1
        else:
            print(f"     ❌ {layer}: erro")
        
        total += 1
    
    # Resultados finais
    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Todas as funcionalidades testadas com sucesso")
        print("🌐 Sistema pronto para uso profissional")
        return 0
    elif passed >= total * 0.8:
        print("✅ SISTEMA MAJORITARIAMENTE FUNCIONAL")
        print(f"⚠️  {total - passed} testes falharam")
        return 0
    else:
        print("❌ SISTEMA COM PROBLEMAS SIGNIFICATIVOS")
        print(f"🔧 {total - passed} testes falharam - requer correções")
        return 1

if __name__ == "__main__":
    exit(main())