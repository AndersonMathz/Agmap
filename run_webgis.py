#!/usr/bin/env python3
"""
WebGIS Launcher - Lançador inteligente do WebGIS
Testa diferentes configurações até encontrar uma que funcione
"""

import os
import sys
import subprocess
import socket
import time

def check_port_free(port):
    """Verifica se uma porta está livre"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except:
        return False

def kill_process_on_port(port):
    """Tenta matar processo na porta (Windows)"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        print(f"🔄 Matando processo {pid} na porta {port}")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        time.sleep(1)
                        return True
    except:
        pass
    return False

def run_server(script_name, port=5001):
    """Executa um servidor específico"""
    if not os.path.exists(script_name):
        return False, f"Arquivo {script_name} não encontrado"
    
    # Verificar se porta está livre
    if not check_port_free(port):
        print(f"⚠️ Porta {port} ocupada, tentando liberar...")
        kill_process_on_port(port)
        time.sleep(2)
        
        if not check_port_free(port):
            return False, f"Porta {port} ainda ocupada"
    
    try:
        print(f"🚀 Iniciando {script_name}...")
        # Usar subprocess para melhor controle
        process = subprocess.Popen([sys.executable, script_name])
        
        # Aguardar um pouco para verificar se iniciou
        time.sleep(3)
        
        # Verificar se o processo ainda está rodando
        if process.poll() is None:
            print(f"✅ {script_name} iniciado com sucesso!")
            print(f"🌐 Acesse: http://localhost:{port}")
            print("🛑 Para parar: Ctrl+C")
            
            # Aguardar o processo
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Parando servidor...")
                process.terminate()
                process.wait()
            
            return True, "Servidor executado com sucesso"
        else:
            return False, f"Processo {script_name} falhou ao iniciar"
            
    except Exception as e:
        return False, f"Erro ao executar {script_name}: {e}"

def main():
    """Função principal do launcher"""
    print("🚀 WebGIS Launcher")
    print("=" * 50)
    
    # Verificar diretório
    if not os.path.exists('templates'):
        print("❌ Execute este script no diretório do WebGIS")
        sys.exit(1)
    
    # Lista de servidores para tentar (em ordem de preferência)
    servers = [
        ('app_fixed.py', 'Servidor Flask Corrigido'),
        ('simple_server.py', 'Servidor Simples'),
        ('app.py', 'Servidor Original'),
        ('debug_server.py', 'Servidor de Debug')
    ]
    
    # Tentar cada servidor
    for script, description in servers:
        print(f"\n🔄 Tentando: {description}")
        
        success, message = run_server(script)
        
        if success:
            print(f"✅ {description} funcionou!")
            break
        else:
            print(f"❌ {description} falhou: {message}")
    
    else:
        print("\n❌ Nenhum servidor conseguiu iniciar!")
        print("\n🔧 Diagnósticos:")
        print("1. Execute: python debug_server.py")
        print("2. Verifique se Flask está instalado: pip install flask")
        print("3. Verifique se a porta 5001 está livre")
        print("4. Execute como administrador")
        
        # Executar diagnósticos automáticos
        try:
            print("\n🔍 Executando diagnósticos...")
            subprocess.run([sys.executable, 'debug_server.py'])
        except:
            print("❌ Não foi possível executar diagnósticos")

if __name__ == '__main__':
    main()