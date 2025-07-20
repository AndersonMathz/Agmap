#!/usr/bin/env python3
"""
WEBAG - Verificador de Dados
Script para verificar dados existentes no banco
"""
import sqlite3
import os
import json

def check_database(db_path):
    """Verifica dados no banco"""
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print(f"=== Verificando {db_path} ===")
            
            # Listar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📊 Tabelas encontradas: {tables}")
            
            # Verificar dados em cada tabela
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  📋 {table}: {count} registros")
                    
                    # Para tabelas pequenas, mostrar alguns dados
                    if count > 0 and count <= 5:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        rows = cursor.fetchall()
                        
                        # Mostrar colunas
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cursor.fetchall()]
                        print(f"    Colunas: {columns}")
                        
                        # Mostrar dados
                        for row in rows:
                            print(f"    Dados: {row}")
                            
                except Exception as e:
                    print(f"  ❌ Erro lendo {table}: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro acessando banco: {e}")
        return False

def main():
    """Função principal"""
    print("=== WEBAG Data Checker ===")
    
    # Verificar banco atual
    current_db = "instance/webgis.db"
    check_database(current_db)
    
    # Verificar se existe banco antigo
    old_dbs = [
        "webgis.db",
        "instance/database.db",
        "database.db"
    ]
    
    for db in old_dbs:
        if os.path.exists(db) and db != current_db:
            print(f"\n🔍 Banco adicional encontrado: {db}")
            check_database(db)

if __name__ == "__main__":
    main()