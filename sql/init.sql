-- WEBAG Professional - Inicialização do Banco de Dados
-- PostgreSQL + PostGIS Setup

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar schema principal
CREATE SCHEMA IF NOT EXISTS webgis;
SET search_path TO webgis, public;

-- Tabela de usuários (versão simplificada para MVP)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    name VARCHAR(255),
    privileges JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de projetos (simplificada)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de features geográficas
CREATE TABLE IF NOT EXISTS geo_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    layer_name VARCHAR(100) NOT NULL,
    feature_type VARCHAR(50),
    geometry GEOMETRY,
    properties JSONB NOT NULL DEFAULT '{}',
    style_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices geoespaciais para performance
CREATE INDEX IF NOT EXISTS idx_geo_features_geometry ON geo_features USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_geo_features_project ON geo_features (project_id);
CREATE INDEX IF NOT EXISTS idx_geo_features_layer ON geo_features (layer_name);

-- Tabela de arquivos uploadados
CREATE TABLE IF NOT EXISTS uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    file_path VARCHAR(500),
    uploaded_by UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    upload_date TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Inserir usuário administrador padrão (senha será hashada pela aplicação)
INSERT INTO users (username, password_hash, email, role, name, privileges) 
VALUES (
    'admin_super',
    'temp_hash_will_be_replaced',
    'admin@webag.com',
    'superuser',
    'Administrador',
    '{"canEditLayers": true, "canManageUsers": true, "canExportData": true, "canViewAllData": true, "canModifyStyles": true, "canDeleteFeatures": true, "canAddNewLayers": true, "canUploadFiles": true}'::jsonb
) ON CONFLICT (username) DO NOTHING;

-- Projeto de exemplo
INSERT INTO projects (name, description, owner_id)
SELECT 
    'Projeto Exemplo',
    'Projeto de demonstração do sistema WebGIS',
    u.id
FROM users u 
WHERE u.username = 'admin_super'
ON CONFLICT DO NOTHING;

-- Configurações do banco
-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Otimizações para desenvolvimento
ALTER SYSTEM SET shared_preload_libraries = 'postgis-3';

COMMENT ON DATABASE webgis_db IS 'WEBAG Professional - Sistema WebGIS para Topografia';
COMMENT ON SCHEMA webgis IS 'Schema principal do sistema WEBAG';

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE 'WEBAG Database initialized successfully!';
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
    RAISE NOTICE 'Users table ready';
    RAISE NOTICE 'Projects table ready';
    RAISE NOTICE 'Geo features table ready';
END $$;