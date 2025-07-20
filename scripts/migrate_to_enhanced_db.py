#!/usr/bin/env python3
"""
WEBAG Professional - Script de Migração para Banco Enhanced
Migra dados existentes para nova estrutura robusta
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_enhanced_database(db_path: str) -> bool:
    """Criar banco de dados com estrutura enhanced"""
    try:
        with open('sql/enhanced_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Executar schema enhanced
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        
        print(f"✅ Banco de dados enhanced criado: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro criando banco enhanced: {e}")
        return False

def migrate_existing_data(old_db_path: str, new_db_path: str) -> bool:
    """Migrar dados do banco antigo para o novo"""
    try:
        # Conectar aos dois bancos
        old_conn = sqlite3.connect(old_db_path)
        new_conn = sqlite3.connect(new_db_path)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        print("🔄 Iniciando migração de dados...")
        
        # 1. Migrar usuários
        print("👥 Migrando usuários...")
        old_cursor.execute("SELECT * FROM users")
        users = old_cursor.fetchall()
        
        org_id = 'org_default'
        for user in users:
            if len(user) >= 4:  # username, password_hash, email, role, name, privileges
                user_id = f"user_{user[0].replace('_', '')}"
                new_cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (id, organization_id, username, email, password_hash, first_name, role, privileges)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, org_id, user[0], user[2] or f"{user[0]}@webag.com", 
                    user[1], user[4] if len(user) > 4 else user[0], 
                    user[3] if len(user) > 3 else 'user',
                    user[5] if len(user) > 5 else '{}'
                ))
        
        # 2. Migrar projetos
        print("📁 Migrando projetos...")
        old_cursor.execute("SELECT * FROM projects")
        projects = old_cursor.fetchall()
        
        for project in projects:
            if len(project) >= 2:
                project_id = f"proj_{project[0] if project[0] else 'default'}"
                new_cursor.execute("""
                    INSERT OR IGNORE INTO projects 
                    (id, organization_id, name, slug, description, owner_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    project_id, org_id, project[1], 
                    project[1].lower().replace(' ', '-'),
                    project[2] if len(project) > 2 else '', 'user_admin'
                ))
        
        # 3. Criar grupos de camadas padrão
        print("📊 Criando grupos de camadas...")
        layer_groups = [
            ('group_base', 'proj_default', 'Camadas Base', 'Camadas base do sistema', 0),
            ('group_osm', 'proj_default', 'OpenStreetMap', 'Dados do OpenStreetMap', 1),
            ('group_glebas', 'proj_default', 'Glebas', 'Glebas cadastradas', 2),
            ('group_analysis', 'proj_default', 'Análises', 'Camadas de análise', 3)
        ]
        
        for group in layer_groups:
            new_cursor.execute("""
                INSERT OR IGNORE INTO layer_groups 
                (id, project_id, name, description, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, group)
        
        # 4. Migrar geo_features para layers e features
        print("🗺️ Migrando features geográficas...")
        old_cursor.execute("SELECT DISTINCT layer_name FROM geo_features WHERE layer_name IS NOT NULL")
        layer_names = [row[0] for row in old_cursor.fetchall()]
        
        layer_mapping = {}
        for i, layer_name in enumerate(layer_names):
            layer_id = f"layer_{i+1:03d}"
            layer_mapping[layer_name] = layer_id
            
            # Determinar grupo baseado no nome
            group_id = 'group_osm'
            if 'gleba' in layer_name.lower():
                group_id = 'group_glebas'
            elif any(word in layer_name.lower() for word in ['base', 'fundo']):
                group_id = 'group_base'
            
            # Determinar tipo de geometria
            old_cursor.execute("""
                SELECT geometry FROM geo_features 
                WHERE layer_name = ? AND geometry IS NOT NULL 
                LIMIT 1
            """, (layer_name,))
            
            geom_row = old_cursor.fetchone()
            geometry_type = 'Polygon'  # Padrão
            
            if geom_row and geom_row[0]:
                try:
                    geom_data = json.loads(geom_row[0])
                    if isinstance(geom_data, dict) and 'type' in geom_data:
                        geometry_type = geom_data['type']
                except:
                    pass
            
            # Inserir layer
            new_cursor.execute("""
                INSERT OR IGNORE INTO layers 
                (id, project_id, layer_group_id, name, display_name, layer_type, 
                 geometry_type, created_by, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                layer_id, 'proj_default', group_id, 
                layer_name.lower().replace(' ', '_'),
                layer_name, 'vector', geometry_type, 'user_admin', i
            ))
        
        # 5. Migrar features
        print("📍 Migrando features individuais...")
        old_cursor.execute("SELECT * FROM geo_features")
        features = old_cursor.fetchall()
        
        feature_count = 0
        for feature in features:
            if len(feature) >= 4 and feature[2]:  # layer_name existe
                layer_id = layer_mapping.get(feature[2])
                if layer_id:
                    feature_id = f"feat_{feature_count+1:06d}"
                    
                    # Determinar tipo de geometria
                    geom_type = 'Polygon'
                    if feature[4]:  # geometry
                        try:
                            geom_data = json.loads(feature[4])
                            if isinstance(geom_data, dict) and 'type' in geom_data:
                                geom_type = geom_data['type']
                        except:
                            pass
                    
                    new_cursor.execute("""
                        INSERT OR IGNORE INTO features 
                        (id, layer_id, feature_type, geometry, properties, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        feature_id, layer_id, geom_type,
                        feature[4] or '{}',  # geometry
                        feature[5] or '{}',  # properties
                        'user_admin'
                    ))
                    
                    feature_count += 1
        
        # 6. Migrar glebas
        print("🏠 Migrando glebas...")
        try:
            old_cursor.execute("SELECT * FROM glebas")
            glebas = old_cursor.fetchall()
            
            for i, gleba in enumerate(glebas):
                if len(gleba) >= 3:
                    # Criar feature para a gleba primeiro
                    feature_id = f"feat_gleba_{i+1:04d}"
                    gleba_id = f"gleba_{i+1:04d}"
                    
                    new_cursor.execute("""
                        INSERT OR IGNORE INTO features 
                        (id, layer_id, feature_type, geometry, properties, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        feature_id, 'layer_001',  # Primeira layer (base)
                        'Polygon',
                        gleba[5] if len(gleba) > 5 else '{}',  # geometry
                        json.dumps({'tipo': 'gleba', 'numero': gleba[1]}),
                        'user_admin'
                    ))
                    
                    # Criar gleba
                    new_cursor.execute("""
                        INSERT OR IGNORE INTO glebas 
                        (id, project_id, feature_id, numero_gleba, nome_gleba, 
                         area_total_m2, perimetro_total_m, proprietario_nome, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        gleba_id, 'proj_default', feature_id,
                        gleba[1],  # no_gleba
                        gleba[2] if len(gleba) > 2 else None,  # nome_gleba
                        gleba[3] if len(gleba) > 3 else None,  # area
                        gleba[4] if len(gleba) > 4 else None,  # perimetro
                        gleba[6] if len(gleba) > 6 else None,  # proprietario
                        'user_admin'
                    ))
                    
        except sqlite3.OperationalError as e:
            if "no such table: glebas" in str(e):
                print("⚠️ Tabela 'glebas' não encontrada no banco antigo - pulando migração de glebas")
            else:
                raise
        
        # Commit e fechar conexões
        new_conn.commit()
        old_conn.close()
        new_conn.close()
        
        print(f"✅ Migração concluída! {feature_count} features migradas")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False

def validate_migration(db_path: str) -> bool:
    """Validar dados migrados"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📊 VALIDAÇÃO DA MIGRAÇÃO:")
        print("=" * 40)
        
        # Contar registros
        tables = [
            'organizations', 'users', 'projects', 'layer_groups', 
            'layers', 'features', 'glebas'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📋 {table}: {count} registros")
            except sqlite3.OperationalError:
                print(f"⚠️ {table}: tabela não encontrada")
        
        # Verificar integridade
        print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE:")
        
        # Verificar se todas as layers têm projeto
        cursor.execute("""
            SELECT COUNT(*) FROM layers l 
            LEFT JOIN projects p ON l.project_id = p.id 
            WHERE p.id IS NULL
        """)
        orphan_layers = cursor.fetchone()[0]
        
        # Verificar se todas as features têm layer
        cursor.execute("""
            SELECT COUNT(*) FROM features f 
            LEFT JOIN layers l ON f.layer_id = l.id 
            WHERE l.id IS NULL
        """)
        orphan_features = cursor.fetchone()[0]
        
        if orphan_layers == 0 and orphan_features == 0:
            print("✅ Integridade referencial OK")
        else:
            print(f"⚠️ Problemas de integridade: {orphan_layers} layers órfãs, {orphan_features} features órfãs")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal do script de migração"""
    print("🚀 WEBAG Professional - Migração para Banco Enhanced")
    print("=" * 60)
    
    # Caminhos dos bancos
    old_db_path = 'instance/webgis.db'
    new_db_path = 'instance/webgis_enhanced.db'
    backup_path = 'instance/webgis_backup.db'
    
    # 1. Verificar se banco antigo existe
    if not os.path.exists(old_db_path):
        print(f"❌ Banco de dados antigo não encontrado: {old_db_path}")
        return False
    
    # 2. Fazer backup do banco antigo
    print(f"💾 Criando backup: {backup_path}")
    try:
        import shutil
        shutil.copy2(old_db_path, backup_path)
        print("✅ Backup criado com sucesso")
    except Exception as e:
        print(f"❌ Erro criando backup: {e}")
        return False
    
    # 3. Criar novo banco enhanced
    if not create_enhanced_database(new_db_path):
        return False
    
    # 4. Migrar dados
    if not migrate_existing_data(old_db_path, new_db_path):
        return False
    
    # 5. Validar migração
    if not validate_migration(new_db_path):
        return False
    
    # 6. Substituir banco antigo (opcional)
    replace_old = input("\n❓ Deseja substituir o banco antigo pelo enhanced? (s/N): ").lower().strip()
    
    if replace_old == 's':
        try:
            # Renomear antigo para .old
            os.rename(old_db_path, f"{old_db_path}.old")
            # Mover enhanced para posição do antigo
            os.rename(new_db_path, old_db_path)
            print("✅ Banco enhanced ativado como principal")
        except Exception as e:
            print(f"❌ Erro substituindo banco: {e}")
            return False
    else:
        print(f"ℹ️ Banco enhanced disponível em: {new_db_path}")
    
    print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 40)
    print("Próximos passos:")
    print("1. Teste o sistema com o novo banco")
    print("2. Verifique todas as funcionalidades")
    print("3. Se tudo estiver OK, remova os backups antigos")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)