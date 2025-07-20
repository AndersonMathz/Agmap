#!/usr/bin/env python3
"""
Inicialização do banco PostgreSQL para produção
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_tables():
    """Criar tabelas básicas no PostgreSQL"""
    
    # SQL para criar tabelas básicas
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS map_features (
            id VARCHAR(255) PRIMARY KEY,
            feature_type VARCHAR(100) NOT NULL,
            geometry TEXT NOT NULL,
            properties TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(80)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_features_type ON map_features(feature_type);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_features_created_by ON map_features(created_by);
        """,
        """
        INSERT INTO users (username, email, password_hash) 
        VALUES ('admin_super', 'admin@webag.com', 'admin123')
        ON CONFLICT (username) DO NOTHING;
        """,
        """
        INSERT INTO users (username, email, password_hash) 
        VALUES ('admin', 'admin2@webag.com', 'admin')
        ON CONFLICT (username) DO NOTHING;
        """
    ]
    
    try:
        # Conectar ao PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🚀 Conectado ao PostgreSQL")
        
        # Executar comandos
        for i, command in enumerate(sql_commands, 1):
            try:
                cursor.execute(command)
                print(f"✅ Comando {i}/{len(sql_commands)} executado")
            except Exception as e:
                print(f"⚠️ Erro no comando {i}: {e}")
        
        cursor.close()
        conn.close()
        
        print("✅ Inicialização do PostgreSQL concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro conectando ao PostgreSQL: {e}")
        return False

if __name__ == '__main__':
    create_tables()