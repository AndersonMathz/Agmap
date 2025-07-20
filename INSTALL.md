# WEBAG Professional - Guia de Instalação

## Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- PostgreSQL 12+ (será configurado no Dia 2)

## Instalação Rápida

### 1. Clone ou use o projeto atual
```bash
cd WEBAG
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 4. Execute a aplicação
```bash
python app.py
```

## Status Atual (Dia 1 Concluído)

✅ **Funcionando:**
- Estrutura de arquivos organizada
- Sistema de autenticação (em memória)
- Funções de validação e segurança
- Templates e assets estáticos

⏳ **Próximos passos (Dia 2):**
- Instalação de dependências Flask
- Configuração PostgreSQL + PostGIS
- Migração de dados
- Sistema web completo funcionando

## Problemas Conhecidos

- Flask não instalado no ambiente atual (normal)
- Banco SQLite temporário (será migrado)
- Usuários em memória (será persistido)

## Suporte

Para problemas de instalação, verifique:
1. Versão do Python: `python --version`
2. Instalação do pip: `pip --version`
3. Permissões de escrita no diretório