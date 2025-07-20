#!/bin/bash
# WEBAG - Setup PostgreSQL Local (alternativo ao Docker)

echo "=== WEBAG PostgreSQL Setup ==="

# Verificar se PostgreSQL está instalado
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL encontrado"
    psql --version
else
    echo "❌ PostgreSQL não encontrado"
    echo "📥 Instruções de instalação:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib postgis"
    echo ""
    echo "Windows:"
    echo "  Download do site oficial: https://www.postgresql.org/download/windows/"
    echo "  Ou use WSL2 com Ubuntu"
    echo ""
    echo "macOS:"
    echo "  brew install postgresql postgis"
    echo ""
    exit 1
fi

# Configurar banco de dados
echo "🔧 Configurando banco de dados..."

# Criar usuário e banco
sudo -u postgres psql -c "CREATE USER webgis_user WITH PASSWORD 'webgis_pass123';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "CREATE DATABASE webgis_db OWNER webgis_user;" 2>/dev/null || echo "Database já existe"
sudo -u postgres psql -d webgis_db -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null

# Executar script de inicialização
if [ -f "sql/init.sql" ]; then
    echo "📄 Executando script de inicialização..."
    sudo -u postgres psql -d webgis_db -f sql/init.sql
    echo "✅ Banco configurado!"
else
    echo "❌ Arquivo sql/init.sql não encontrado"
fi

# Testar conexão
echo "🧪 Testando conexão..."
PGPASSWORD=webgis_pass123 psql -h localhost -U webgis_user -d webgis_db -c "SELECT version();" && echo "✅ Conexão OK"

echo "=== Setup concluído ==="
echo "Connection string: postgresql://webgis_user:webgis_pass123@localhost:5432/webgis_db"