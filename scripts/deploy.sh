#!/bin/bash

# Script de Deploy para WebGIS em Produção
# Execute como root ou com sudo

set -e

echo "🚀 Iniciando deploy do WebGIS..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root ou com sudo"
    exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "📦 Instalando dependências..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Criar usuário para aplicação
echo "👤 Criando usuário webgis..."
if ! id "webgis" &>/dev/null; then
    useradd -m -s /bin/bash webgis
fi

# Criar diretório da aplicação
APP_DIR="/opt/webgis"
echo "📁 Criando diretório da aplicação: $APP_DIR"
mkdir -p $APP_DIR
chown webgis:webgis $APP_DIR

# Copiar arquivos da aplicação
echo "📋 Copiando arquivos da aplicação..."
cp -r . $APP_DIR/
chown -R webgis:webgis $APP_DIR

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
cd $APP_DIR
sudo -u webgis python3 -m venv venv
sudo -u webgis ./venv/bin/pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/logs
chown -R webgis:webgis $APP_DIR/uploads
chown -R webgis:webgis $APP_DIR/logs

# Configurar arquivo .env
echo "⚙️ Configurando variáveis de ambiente..."
if [ ! -f $APP_DIR/.env ]; then
    cp $APP_DIR/env_example.txt $APP_DIR/.env
    # Gerar chave secreta
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/sua-chave-secreta-muito-segura-aqui-mude-para-producao/$SECRET_KEY/" $APP_DIR/.env
    chown webgis:webgis $APP_DIR/.env
fi

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cp $APP_DIR/nginx.conf /etc/nginx/sites-available/webgis
ln -sf /etc/nginx/sites-available/webgis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
nginx -t

# Configurar systemd service
echo "🔧 Configurando serviço systemd..."
cat > /etc/systemd/system/webgis.service << EOF
[Unit]
Description=WebGIS Application
After=network.target

[Service]
Type=notify
User=webgis
Group=webgis
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e habilitar serviço
systemctl daemon-reload
systemctl enable webgis
systemctl start webgis

# Reiniciar Nginx
systemctl restart nginx

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

echo "✅ Deploy concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure seu domínio no arquivo nginx.conf"
echo "2. Execute: certbot --nginx -d seu-dominio.com"
echo "3. Acesse: https://seu-dominio.com"
echo ""
echo "🔧 Comandos úteis:"
echo "  - Verificar status: systemctl status webgis"
echo "  - Ver logs: journalctl -u webgis -f"
echo "  - Reiniciar: systemctl restart webgis" 