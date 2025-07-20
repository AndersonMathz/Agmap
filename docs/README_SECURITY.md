# WebGIS - Guia de Segurança para Produção

## 🚀 Deploy Seguro em Produção

Este guia fornece instruções completas para implantar o WebGIS de forma segura em produção.

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- Domínio configurado com DNS
- Acesso root ou sudo
- Python 3.8+

## 🔧 Instalação Rápida

### 1. Clone e Prepare

```bash
git clone <seu-repositorio>
cd webgis
chmod +x deploy.sh
```

### 2. Configure o Domínio

Edite o arquivo `nginx.conf` e substitua `seu-dominio.com` pelo seu domínio real.

### 3. Execute o Deploy

```bash
sudo ./deploy.sh
```

### 4. Configure SSL

```bash
sudo certbot --nginx -d seu-dominio.com
```

## 🔒 Medidas de Segurança Implementadas

### Autenticação e Autorização
- ✅ Autenticação no backend (Flask)
- ✅ Senhas criptografadas (bcrypt)
- ✅ Sessões seguras (HttpOnly, Secure, SameSite)
- ✅ Controle de acesso baseado em privilégios

### Proteção contra Ataques
- ✅ XSS: Sanitização de entrada e escape de HTML
- ✅ CSRF: Tokens de proteção
- ✅ Path Traversal: Validação de caminhos
- ✅ SQL Injection: Queries parametrizadas
- ✅ File Upload: Validação de tipos e conteúdo

### Headers de Segurança
- ✅ X-Content-Type-Options: nosniff
- ✅ X-Frame-Options: DENY
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Strict-Transport-Security
- ✅ Content-Security-Policy

### Configurações de Servidor
- ✅ HTTPS obrigatório
- ✅ Rate limiting (100 req/hora)
- ✅ Timeouts configurados
- ✅ Logs de segurança
- ✅ Firewall configurado

## 🧪 Testando a Segurança

### Executar Testes Automáticos

```bash
python3 test_security.py
```

### Testes Manuais Recomendados

1. **Autenticação**
   - Tentar acessar sem login
   - Testar credenciais inválidas
   - Verificar logout

2. **Upload de Arquivos**
   - Tentar upload de arquivos não-KML
   - Testar arquivos com conteúdo malicioso
   - Verificar validação de tamanho

3. **Headers de Segurança**
   - Verificar se HTTPS redireciona HTTP
   - Confirmar headers de segurança
   - Testar CSP

## 📁 Estrutura de Arquivos Segura

```
/opt/webgis/
├── app.py              # Aplicação principal
├── config.py           # Configurações
├── models.py           # Modelos de usuário
├── utils.py            # Utilitários de segurança
├── templates/          # Templates HTML
├── static/             # Arquivos estáticos
├── uploads/            # Uploads de usuários (isolado)
├── logs/               # Logs de segurança
├── .env                # Variáveis de ambiente (protegido)
└── venv/               # Ambiente virtual
```

## 🔧 Configuração de Ambiente

### Variáveis de Ambiente (.env)

```bash
# Gerar chave secreta única
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Configurar ambiente
FLASK_ENV=production
DATABASE_URL=sqlite:///webgis.db
CORS_ORIGINS=https://seudominio.com
```

### Usuários Padrão

- **Superusuário**: `admin_super` / `isis/2020`
- **Usuário**: `admin` / `admin`

**⚠️ IMPORTANTE**: Altere essas senhas em produção!

## 📊 Monitoramento

### Logs de Segurança

```bash
# Ver logs em tempo real
tail -f /opt/webgis/logs/webgis.log

# Ver logs do sistema
journalctl -u webgis -f

# Ver logs do Nginx
tail -f /var/log/nginx/webgis_access.log
```

### Alertas Recomendados

- Tentativas de login falhadas
- Uploads de arquivos suspeitos
- Acessos não autorizados
- Erros de validação

## 🔄 Manutenção

### Atualizações Regulares

```bash
# Atualizar dependências
cd /opt/webgis
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Reiniciar serviço
sudo systemctl restart webgis
```

### Backup

```bash
# Backup dos dados
tar -czf webgis-backup-$(date +%Y%m%d).tar.gz /opt/webgis/uploads /opt/webgis/webgis.db
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro 502 Bad Gateway**
   ```bash
   sudo systemctl status webgis
   sudo journalctl -u webgis -n 50
   ```

2. **SSL não funciona**
   ```bash
   sudo certbot renew --dry-run
   sudo nginx -t
   ```

3. **Upload não funciona**
   ```bash
   sudo chown -R webgis:webgis /opt/webgis/uploads
   sudo chmod 755 /opt/webgis/uploads
   ```

## 📞 Suporte

Para questões de segurança:
- Revise os logs de segurança
- Execute o script de testes
- Consulte a documentação SECURITY.md

## 📝 Checklist de Deploy

- [ ] Domínio configurado
- [ ] SSL certificado
- [ ] Firewall ativo
- [ ] Senhas alteradas
- [ ] Logs configurados
- [ ] Backup configurado
- [ ] Testes de segurança passaram
- [ ] Monitoramento ativo

## 🔐 Próximos Passos

1. Configure monitoramento avançado (Sentry, Loggly)
2. Implemente autenticação 2FA
3. Configure backup automático
4. Implemente auditoria completa
5. Configure alertas de segurança

---

**⚠️ AVISO**: Este sistema foi desenvolvido seguindo as melhores práticas de segurança, mas a segurança é um processo contínuo. Mantenha-se atualizado e monitore regularmente. 