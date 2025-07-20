#!/usr/bin/env python3
"""
WEBAG - Inicializador do banco SQLite
Script para criar e popular o banco de dados SQLite
"""
import sqlite3
import os
import json
from datetime import datetime

# Configurações
DB_PATH = "instance/webgis.db"
SQL_SCRIPT = "sql/sqlite_init.sql"

def ensure_instance_directory():
    """Garante que o diretório instance existe"""
    os.makedirs("instance", exist_ok=True)

def execute_sql_script(db_path, script_path):
    """Executa script SQL no banco"""
    if not os.path.exists(script_path):
        print(f"❌ Script SQL não encontrado: {script_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            
            # Executar script
            conn.executescript(script)
            print(f"✅ Script executado: {script_path}")
            return True
            
    except Exception as e:
        print(f"❌ Erro executando script: {e}")
        return False

def update_admin_password(db_path, new_password_hash):
    """Atualiza hash da senha do admin"""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = 'admin_super'",
                (new_password_hash,)
            )
            print("✅ Senha do admin atualizada")
            return True
    except Exception as e:
        print(f"❌ Erro atualizando senha: {e}")
        return False

def verify_database(db_path):
    """Verifica se o banco foi criado corretamente"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"📊 Tabelas criadas: {', '.join(tables)}")
            
            # Verificar dados
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM projects")
            projects_count = cursor.fetchone()[0]
            
            print(f"👥 Usuários: {users_count}")
            print(f"📁 Projetos: {projects_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro verificando banco: {e}")
        return False

def main():
    """Função principal"""
    print("=== WEBAG SQLite Database Initializer ===")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Criar diretório instance
    ensure_instance_directory()
    
    # Executar script de inicialização
    if not execute_sql_script(DB_PATH, SQL_SCRIPT):
        return 1
    
    # Simular hash de senha (em produção, use bcrypt)
    admin_password_hash = "hashed_password_replace_with_bcrypt"
    update_admin_password(DB_PATH, admin_password_hash)
    
    # Verificar banco
    if verify_database(DB_PATH):
        print("🎉 Banco SQLite inicializado com sucesso!")
        print(f"📍 Localização: {os.path.abspath(DB_PATH)}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())