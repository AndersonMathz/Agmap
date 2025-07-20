#!/usr/bin/env python3
"""
Script para reiniciar o servidor WebGIS com cache limpo
"""
import os
import sys
import subprocess
import time

def kill_existing_servers():
    """Mata todos os processos Flask existentes"""
    try:
        subprocess.run(["pkill", "-f", "python.*app.py"], check=False)
        subprocess.run(["pkill", "-f", "flask"], check=False)
        time.sleep(2)
        print("✅ Processos Flask anteriores finalizados")
    except Exception as e:
        print(f"⚠️  Aviso: {e}")

def clear_python_cache():
    """Limpa cache do Python"""
    try:
        # Remover arquivos .pyc
        subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], check=False)
        # Remover diretórios __pycache__
        subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"], check=False)
        print("✅ Cache Python limpo")
    except Exception as e:
        print(f"⚠️  Aviso ao limpar cache Python: {e}")

def start_server():
    """Inicia o servidor Flask"""
    print("🚀 Iniciando servidor WebGIS...")
    print("=" * 50)
    
    # Ativar virtual environment e iniciar servidor
    venv_python = "./venv/bin/python"
    if os.path.exists(venv_python):
        subprocess.run([venv_python, "app.py"])
    else:
        subprocess.run(["python3", "app.py"])

if __name__ == "__main__":
    print("🔄 Reiniciando WebGIS Server...")
    
    # Mudar para diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    kill_existing_servers()
    clear_python_cache()
    start_server()