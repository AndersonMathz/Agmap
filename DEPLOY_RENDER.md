# 🚀 DEPLOY NO RENDER - WEBAG Professional

## 📋 **Configuração Rápida**

### **1. Conectar Repositório**
1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New Web Service"
3. Conecte seu repositório GitHub: `https://github.com/AndersonMathz/Agmap`

### **2. Configurações do Serviço**
```
Name: webag-professional
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

### **3. Variáveis de Ambiente**
Configure essas variáveis no Render:

```env
FLASK_ENV=production
SECRET_KEY=[gerado automaticamente pelo Render]
DATABASE_URL=[URL do PostgreSQL do Render]
PORT=10000
PYTHONPATH=/opt/render/project/src
```

### **4. Banco de Dados PostgreSQL**
1. Crie um PostgreSQL Database no Render
2. Copie a CONNECTION STRING
3. Cole em DATABASE_URL nas variáveis de ambiente

### **5. Deploy Automático**
```bash
# Fazer push das mudanças
git add .
git commit -m "Configuração para deploy no Render"
git push origin master
```

## ⚙️ **Configurações Específicas**

### **Arquivos Críticos:**
- ✅ `wsgi.py` - Entry point WSGI
- ✅ `Procfile` - Comando de start 
- ✅ `render.yaml` - Configuração automática
- ✅ `requirements.txt` - Dependências
- ✅ `config/config.py` - Configurações de produção

### **Estrutura de Arquivos:**
```
webag/
├── wsgi.py              # WSGI entry point
├── Procfile             # Comando do servidor
├── render.yaml          # Configuração do Render
├── requirements.txt     # Dependências Python
├── config/config.py     # Configurações
└── app/                 # Aplicação Flask
```

## 🔧 **Troubleshooting**

### **Problema: "No module named 'app'"**
- ✅ Verificar se `PYTHONPATH` está configurado
- ✅ Verificar se `wsgi.py` tem fallback de import

### **Problema: "Database connection failed"**
- ✅ Verificar se `DATABASE_URL` está configurado
- ✅ Verificar se PostgreSQL database foi criado

### **Problema: "Port already in use"**
- ✅ Verificar se `PORT` environment variable está sendo usada
- ✅ Comando deve usar `--bind 0.0.0.0:$PORT`

## 📊 **Monitoramento**

### **Logs em Tempo Real:**
```bash
# No dashboard do Render
Logs -> View Logs (últimas 24h)
```

### **Métricas:**
- CPU e Memória no dashboard
- Response time 
- Uptime status

## 🎯 **Próximos Passos**

1. **Deploy básico funcionando** ✅
2. **Configurar domínio customizado**
3. **Configurar HTTPS (automático no Render)**
4. **Configurar backup do banco**
5. **Implementar monitoramento avançado**

## 🔗 **URLs Úteis**

- **Dashboard:** https://dashboard.render.com
- **Documentação:** https://render.com/docs
- **Status:** https://status.render.com