#!/usr/bin/env python3
"""
Inicializador simples para o WebGIS
Execute este arquivo para iniciar o servidor automaticamente
"""

import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

def main():
    print("🚀 Iniciando WebGIS...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app.py'):
        print("❌ Erro: Arquivo app.py não encontrado!")
        print("Certifique-se de estar na pasta correta do projeto.")
        return
    
    # Verificar se os arquivos necessários existem
    required_files = ['app.py', 'config.py', 'models.py', 'utils.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Arquivos necessários não encontrados:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ Arquivos verificados com sucesso!")
    print("🌐 Iniciando servidor Flask...")
    print("=" * 50)
    
    # Aguardar um pouco para o servidor inicializar
    time.sleep(2)
    
    # Abrir navegador
    try:
        print("🌐 Abrindo navegador...")
        webbrowser.open('http://localhost:5000/login')
        print("✅ Navegador aberto!")
    except Exception as e:
        print(f"⚠️ Não foi possível abrir o navegador: {e}")
        print("Acesse manualmente: http://localhost:5000/login")
    
    print("=" * 50)
    print("📋 Instruções:")
    print("1. Faça login com suas credenciais")
    print("2. Use os controles na sidebar para navegar")
    print("3. Para parar o servidor, feche este terminal")
    print("=" * 50)
    
    # Iniciar o servidor Flask
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main() 