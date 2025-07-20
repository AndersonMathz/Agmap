#!/usr/bin/env python3
"""
Script de teste para verificar o login do WebGIS
"""

import requests
import json

def test_login():
    """Testar o sistema de login"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testando sistema de login...")
    
    # Teste 1: Verificar se a página de login está acessível
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✅ Página de login: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar página de login: {e}")
        return
    
    # Teste 2: Tentar login com credenciais corretas
    try:
        login_data = {
            'username': 'admin_super',
            'password': 'isis/2020'
        }
        
        response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"✅ Login POST: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Resposta: {json.dumps(data, indent=2)}")
                
                if data.get('success'):
                    print("🎉 Login bem-sucedido!")
                else:
                    print(f"❌ Login falhou: {data.get('error')}")
            except json.JSONDecodeError:
                print("⚠️ Resposta não é JSON válido")
                print(f"📄 Conteúdo: {response.text[:200]}...")
        else:
            print(f"❌ Status code inesperado: {response.status_code}")
            print(f"📄 Conteúdo: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
    
    # Teste 3: Verificar API de autenticação
    try:
        response = requests.get(f"{base_url}/api/auth/check")
        print(f"✅ API auth check: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Usuário autenticado: {data.get('user', {}).get('username')}")
        else:
            print("ℹ️ Usuário não autenticado (esperado)")
            
    except Exception as e:
        print(f"❌ Erro na API auth check: {e}")

if __name__ == "__main__":
    test_login() 