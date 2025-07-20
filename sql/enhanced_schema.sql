-- ================================================
-- WEBAG PROFESSIONAL - ENHANCED DATABASE SCHEMA
-- Banco de Dados Robusto com Gestão Avançada de Camadas
-- ================================================

-- Habilitar foreign keys e extensões
PRAGMA foreign_keys = ON;

-- ================================================
-- CORE TABLES - Estrutura Principal
-- ================================================

-- Organizações (Multi-tenant support)
CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    logo_url VARCHAR(500),
    settings TEXT DEFAULT '{}', -- JSON configurações
    subscription_plan VARCHAR(50) DEFAULT 'free',
    max_users INTEGER DEFAULT 10,
    max_projects INTEGER DEFAULT 5,
    max_storage_mb INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Usuários (Enhanced)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    privileges TEXT DEFAULT '{}', -- JSON permissões específicas
    avatar_url VARCHAR(500),
    last_login_at DATETIME,
    login_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,
    two_factor_enabled BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, username),
    UNIQUE(organization_id, email)
);

-- Projetos (Enhanced)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    organization_id TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    project_type VARCHAR(50) DEFAULT 'topography', -- topography, cadastre, planning
    bbox_coordinates TEXT, -- JSON bounding box
    default_projection VARCHAR(20) DEFAULT 'EPSG:4326',
    thumbnail_url VARCHAR(500),
    settings TEXT DEFAULT '{}', -- JSON configurações do projeto
    status VARCHAR(20) DEFAULT 'active', -- active, archived, deleted
    owner_id TEXT NOT NULL REFERENCES users(id),
    visibility VARCHAR(20) DEFAULT 'private', -- public, private, organization
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, slug)
);

-- ================================================
-- LAYER MANAGEMENT - Sistema Robusto de Camadas
-- ================================================

-- Grupos de Camadas (Hierarquia)
CREATE TABLE IF NOT EXISTS layer_groups (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parent_group_id TEXT REFERENCES layer_groups(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_expanded BOOLEAN DEFAULT 1,
    is_visible BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Definição de Camadas (Metadados)
CREATE TABLE IF NOT EXISTS layers (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    layer_group_id TEXT REFERENCES layer_groups(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    layer_type VARCHAR(50) NOT NULL, -- vector, raster, wms, wfs, geojson
    geometry_type VARCHAR(50), -- Point, LineString, Polygon, MultiPolygon
    source_type VARCHAR(50) DEFAULT 'internal', -- internal, external, service
    source_url VARCHAR(1000), -- Para WMS/WFS externos
    source_config TEXT DEFAULT '{}', -- JSON configuração da fonte
    
    -- Configurações visuais
    default_style TEXT DEFAULT '{}', -- JSON estilo padrão
    min_zoom INTEGER DEFAULT 0,
    max_zoom INTEGER DEFAULT 18,
    opacity REAL DEFAULT 1.0,
    
    -- Metadados
    srid VARCHAR(20) DEFAULT 'EPSG:4326',
    bbox_coordinates TEXT, -- JSON bounding box da camada
    feature_count INTEGER DEFAULT 0,
    file_size_bytes INTEGER DEFAULT 0,
    
    -- Schema de atributos (para validação)
    schema_definition TEXT DEFAULT '{}', -- JSON schema dos atributos
    
    -- Controle de acesso
    is_public BOOLEAN DEFAULT 0,
    is_editable BOOLEAN DEFAULT 1,
    is_deletable BOOLEAN DEFAULT 1,
    edit_permissions TEXT DEFAULT '{}', -- JSON permissões específicas
    
    -- Status e ordem
    status VARCHAR(20) DEFAULT 'active', -- active, hidden, archived
    display_order INTEGER DEFAULT 0,
    is_visible BOOLEAN DEFAULT 1,
    is_selectable BOOLEAN DEFAULT 1,
    
    -- Auditoria
    created_by TEXT NOT NULL REFERENCES users(id),
    updated_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(project_id, name)
);

-- ================================================
-- FEATURE MANAGEMENT - Gestão Avançada de Features
-- ================================================

-- Features Geográficas (Enhanced)
CREATE TABLE IF NOT EXISTS features (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    layer_id TEXT NOT NULL REFERENCES layers(id) ON DELETE CASCADE,
    feature_type VARCHAR(50) NOT NULL, -- Point, LineString, Polygon, etc
    geometry TEXT NOT NULL, -- GeoJSON geometry
    properties TEXT DEFAULT '{}', -- JSON propriedades
    style_override TEXT DEFAULT '{}', -- JSON estilo específico para este feature
    
    -- Metadados calculados
    area_m2 REAL, -- Área em metros quadrados (se aplicável)
    length_m REAL, -- Comprimento em metros (se aplicável)
    perimeter_m REAL, -- Perímetro em metros (se aplicável)
    centroid_coordinates TEXT, -- JSON coordenadas do centroide
    
    -- Versionamento
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT 1,
    parent_feature_id TEXT REFERENCES features(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, deleted, archived
    validation_status VARCHAR(20) DEFAULT 'valid', -- valid, invalid, pending
    validation_errors TEXT, -- JSON erros de validação
    
    -- Auditoria
    created_by TEXT NOT NULL REFERENCES users(id),
    updated_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- SPECIALIZED TABLES - Tabelas Especializadas
-- ================================================

-- Glebas (Enhanced para Topografia)
CREATE TABLE IF NOT EXISTS glebas (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    feature_id TEXT NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    
    -- Identificação
    numero_gleba VARCHAR(50) NOT NULL,
    nome_gleba VARCHAR(255),
    tipo_gleba VARCHAR(50) DEFAULT 'urbana', -- urbana, rural, industrial
    
    -- Medições (calculadas automaticamente)
    area_total_m2 REAL,
    area_construida_m2 REAL,
    perimetro_total_m REAL,
    
    -- Testadas (calculadas automaticamente)
    testada_frente_m REAL,
    testada_fundo_m REAL,
    testada_esquerda_m REAL,
    testada_direita_m REAL,
    
    -- Confrontações
    confrontacao_frente TEXT,
    confrontacao_fundo TEXT,
    confrontacao_esquerda TEXT,
    confrontacao_direita TEXT,
    
    -- Proprietário
    proprietario_nome VARCHAR(255),
    proprietario_cpf_cnpj VARCHAR(18),
    proprietario_rg VARCHAR(20),
    proprietario_email VARCHAR(255),
    proprietario_telefone VARCHAR(20),
    
    -- Endereço
    endereco_logradouro VARCHAR(300),
    endereco_numero VARCHAR(20),
    endereco_complemento VARCHAR(100),
    endereco_bairro VARCHAR(100),
    endereco_cidade VARCHAR(100),
    endereco_uf VARCHAR(2),
    endereco_cep VARCHAR(9),
    endereco_quadra VARCHAR(50),
    endereco_lote VARCHAR(50),
    
    -- Informações Legais
    matricula_registro VARCHAR(100),
    cartorio_registro VARCHAR(255),
    inscricao_municipal VARCHAR(100),
    inscricao_estadual VARCHAR(100),
    iptu_numero VARCHAR(100),
    
    -- Informações Financeiras
    valor_venal REAL,
    valor_mercado REAL,
    valor_iptu REAL,
    
    -- Uso do Solo
    uso_atual VARCHAR(100),
    uso_permitido VARCHAR(100),
    zoneamento VARCHAR(50),
    coeficiente_aproveitamento REAL,
    taxa_ocupacao REAL,
    
    -- Observações e Anotações
    observacoes TEXT,
    anotacoes_tecnicas TEXT,
    
    -- Status e Validação
    status_aprovacao VARCHAR(20) DEFAULT 'rascunho', -- rascunho, aprovado, rejeitado
    validado_por TEXT REFERENCES users(id),
    validado_em DATETIME,
    
    -- Auditoria
    created_by TEXT NOT NULL REFERENCES users(id),
    updated_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(project_id, numero_gleba)
);

-- ================================================
-- AUDIT & VERSIONING - Auditoria e Versionamento
-- ================================================

-- Log de Alterações (Auditoria Completa)
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    table_name VARCHAR(100) NOT NULL,
    record_id TEXT NOT NULL,
    operation VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values TEXT, -- JSON valores antigos
    new_values TEXT, -- JSON valores novos
    changed_fields TEXT, -- JSON lista de campos alterados
    user_id TEXT REFERENCES users(id),
    user_ip VARCHAR(45),
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Histórico de Layers (Versionamento)
CREATE TABLE IF NOT EXISTS layer_versions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    layer_id TEXT NOT NULL REFERENCES layers(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    version_name VARCHAR(100),
    description TEXT,
    layer_config TEXT NOT NULL, -- JSON snapshot completo da layer
    feature_count INTEGER DEFAULT 0,
    created_by TEXT NOT NULL REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(layer_id, version_number)
);

-- ================================================
-- PERFORMANCE INDEXES - Índices para Performance
-- ================================================

-- Índices principais
CREATE INDEX IF NOT EXISTS idx_users_org_username ON users(organization_id, username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_projects_org_owner ON projects(organization_id, owner_id);
CREATE INDEX IF NOT EXISTS idx_layers_project ON layers(project_id);
CREATE INDEX IF NOT EXISTS idx_layers_group ON layers(layer_group_id);
CREATE INDEX IF NOT EXISTS idx_layers_type ON layers(layer_type);
CREATE INDEX IF NOT EXISTS idx_features_layer ON features(layer_id);
CREATE INDEX IF NOT EXISTS idx_features_current ON features(is_current);
CREATE INDEX IF NOT EXISTS idx_glebas_project ON glebas(project_id);
CREATE INDEX IF NOT EXISTS idx_glebas_feature ON glebas(feature_id);
CREATE INDEX IF NOT EXISTS idx_audit_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

-- Índices compostos para queries específicas
CREATE INDEX IF NOT EXISTS idx_layers_project_visible ON layers(project_id, is_visible, display_order);
CREATE INDEX IF NOT EXISTS idx_features_layer_current ON features(layer_id, is_current, status);

-- ================================================
-- TRIGGERS - Automação e Integridade
-- ================================================

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER IF NOT EXISTS update_organizations_timestamp 
    AFTER UPDATE ON organizations
BEGIN
    UPDATE organizations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
    AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_layers_timestamp 
    AFTER UPDATE ON layers
BEGIN
    UPDATE layers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_features_timestamp 
    AFTER UPDATE ON features
BEGIN
    UPDATE features SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_glebas_timestamp 
    AFTER UPDATE ON glebas
BEGIN
    UPDATE glebas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger para contagem automática de features
CREATE TRIGGER IF NOT EXISTS update_layer_feature_count_insert
    AFTER INSERT ON features
BEGIN
    UPDATE layers 
    SET feature_count = (
        SELECT COUNT(*) FROM features 
        WHERE layer_id = NEW.layer_id AND is_current = 1 AND status = 'active'
    )
    WHERE id = NEW.layer_id;
END;

CREATE TRIGGER IF NOT EXISTS update_layer_feature_count_update
    AFTER UPDATE ON features
BEGIN
    UPDATE layers 
    SET feature_count = (
        SELECT COUNT(*) FROM features 
        WHERE layer_id = NEW.layer_id AND is_current = 1 AND status = 'active'
    )
    WHERE id = NEW.layer_id;
END;

CREATE TRIGGER IF NOT EXISTS update_layer_feature_count_delete
    AFTER DELETE ON features
BEGIN
    UPDATE layers 
    SET feature_count = (
        SELECT COUNT(*) FROM features 
        WHERE layer_id = OLD.layer_id AND is_current = 1 AND status = 'active'
    )
    WHERE id = OLD.layer_id;
END;

-- ================================================
-- INITIAL DATA - Dados Iniciais
-- ================================================

-- Organização padrão
INSERT OR IGNORE INTO organizations (
    id, name, slug, description, subscription_plan, max_users, max_projects, max_storage_mb
) VALUES (
    'org_default', 
    'WEBAG Professional', 
    'webag-default',
    'Organização padrão do sistema WEBAG Professional',
    'enterprise',
    100,
    50,
    10000
);

-- Usuário administrador
INSERT OR IGNORE INTO users (
    id, organization_id, username, email, password_hash, first_name, last_name, role, privileges
) VALUES (
    'user_admin',
    'org_default',
    'admin_super',
    'admin@webag.com',
    'temp_hash_will_be_replaced',
    'Administrador',
    'Sistema',
    'superuser',
    '{"canManageOrganization": true, "canManageUsers": true, "canManageProjects": true, "canManageLayers": true, "canEditLayers": true, "canDeleteLayers": true, "canExportData": true, "canImportData": true, "canViewAuditLog": true, "canManageSystem": true}'
);

-- Projeto padrão
INSERT OR IGNORE INTO projects (
    id, organization_id, name, slug, description, project_type, owner_id
) VALUES (
    'proj_default',
    'org_default',
    'Projeto Principal',
    'projeto-principal',
    'Projeto principal do sistema WEBAG com dados de exemplo',
    'topography',
    'user_admin'
);

-- Grupo de camadas padrão
INSERT OR IGNORE INTO layer_groups (
    id, project_id, name, description, display_order
) VALUES 
    ('group_base', 'proj_default', 'Camadas Base', 'Camadas base do sistema', 0),
    ('group_cadastre', 'proj_default', 'Cadastro', 'Camadas de cadastro urbano', 1),
    ('group_topography', 'proj_default', 'Topografia', 'Camadas topográficas', 2),
    ('group_analysis', 'proj_default', 'Análises', 'Camadas de análise e resultados', 3);

-- Verificação final
SELECT 'Enhanced Database Schema Initialized Successfully' as status;