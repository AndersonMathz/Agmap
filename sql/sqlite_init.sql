-- WEBAG Professional - Schema SQLite (Fallback)
-- Compatível com migração para PostgreSQL

-- Habilitar foreign keys
PRAGMA foreign_keys = ON;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    name VARCHAR(255),
    privileges TEXT DEFAULT '{}', -- JSON como TEXT no SQLite
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de projetos
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de features geográficas (geometria como GeoJSON TEXT)
CREATE TABLE IF NOT EXISTS geo_features (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT REFERENCES projects(id),
    layer_name VARCHAR(100) NOT NULL,
    feature_type VARCHAR(50),
    geometry TEXT, -- GeoJSON como TEXT
    properties TEXT NOT NULL DEFAULT '{}', -- JSON como TEXT
    style_config TEXT DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de arquivos uploadados
CREATE TABLE IF NOT EXISTS uploaded_files (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_path VARCHAR(500),
    uploaded_by TEXT REFERENCES users(id),
    project_id TEXT REFERENCES projects(id),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_geo_features_project ON geo_features (project_id);
CREATE INDEX IF NOT EXISTS idx_geo_features_layer ON geo_features (layer_name);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects (owner_id);

-- Triggers para updated_at
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

CREATE TRIGGER IF NOT EXISTS update_geo_features_timestamp 
    AFTER UPDATE ON geo_features
BEGIN
    UPDATE geo_features SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Inserir usuário administrador padrão
INSERT OR IGNORE INTO users (
    username, password_hash, email, role, name, privileges
) VALUES (
    'admin_super',
    'temp_hash_will_be_replaced',
    'admin@webag.com',
    'superuser',
    'Administrador',
    '{"canEditLayers": true, "canManageUsers": true, "canExportData": true, "canViewAllData": true, "canModifyStyles": true, "canDeleteFeatures": true, "canAddNewLayers": true, "canUploadFiles": true}'
);

-- Projeto de exemplo
INSERT OR IGNORE INTO projects (name, description, owner_id)
SELECT 
    'Projeto Exemplo',
    'Projeto de demonstração do sistema WebGIS',
    u.id
FROM users u 
WHERE u.username = 'admin_super';

-- Verificações
SELECT 'Database initialized' as status;
SELECT 'Users table: ' || COUNT(*) || ' records' as users_count FROM users;
SELECT 'Projects table: ' || COUNT(*) || ' records' as projects_count FROM projects;