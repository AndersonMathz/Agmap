# 🗺️ WEBAG Professional - Sistema WebGIS para Topografia

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

Um sistema WebGIS moderno e profissional desenvolvido especificamente para topógrafos e engenheiros, com interface web responsiva e ferramentas específicas para levantamentos topográficos.

> **📋 Nota**: Este repositório serve como base para desenvolvimento e backup da aplicação Web AG.

## 🚀 **Funcionalidades**

### **📊 Visualização de Dados**
- 🗺️ **Mapas Interativos** com Leaflet.js
- 📍 **61.499+ Features Geográficas** pré-carregadas
- 🏗️ **4 Camadas Especializadas**: Edifícios, Estradas, Lugares, Setores Censitários
- 🔍 **Controle de Camadas** dinâmico

### **🛠️ Ferramentas de Topografia**
- 📏 **Medição de Distâncias** precisas
- 📐 **Cálculo de Áreas** em tempo real
- 🎯 **Sistema de Coordenadas** WGS84
- 📊 **Relatórios Estatísticos** automatizados
- 📁 **Exportação KML** para CAD

### **🔧 APIs REST Completas**
- ✅ `GET /api/health` - Health check do sistema
- 📈 `GET /api/features/stats` - Estatísticas por camada
- 🗂️ `GET /api/layers` - Lista de camadas disponíveis
- 📍 `GET /api/features` - Features geográficas
- 🏢 `GET /api/projects` - Gestão de projetos

## 🖥️ **Screenshots**

*Interface principal mostrando visualização de dados topográficos com ferramentas profissionais*

## ⚡ **Instalação Rápida**

### **Pré-requisitos**
- Python 3.8+
- Navegador moderno (Chrome, Firefox, Safari, Edge)

### **Execução Imediata**
```bash
# Clone o repositório
git clone https://github.com/AndersonMathz/web_ag.git
cd web_ag

# Execute o servidor (sem dependências externas)
python3 simple_flask.py
```

### **Acesse o Sistema**
- 🌐 **Interface Principal**: http://localhost:5000
- 📊 **API Status**: http://localhost:5000/api/health

## 🔧 **Instalação Completa (Opcional)**

Para funcionalidades avançadas com Flask:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor Flask
python3 app.py

# Ou usar Docker
docker-compose up
```

## 📁 **Estrutura do Projeto**

```
WEBAG/
├── 🐍 simple_flask.py          # Servidor web simples (sem deps)
├── 🌐 app.py                   # Servidor Flask completo
├── 📁 app/                     # Core da aplicação
│   ├── models/                 # Modelos de dados
│   ├── views/                  # Controllers
│   ├── services/               # Lógica de negócio
│   └── utils/                  # Utilitários
├── 🎨 templates/               # Templates HTML
├── 📱 static/                  # CSS, JS, assets
├── 🗄️ sql/                     # Scripts de banco
├── ⚙️ config/                  # Configurações
├── 🧪 tests/                   # Testes automatizados
├── 📊 data/                    # Dados geográficos
└── 📚 docs/                    # Documentação
```

## 🎯 **Casos de Uso**

### **Para Topógrafos**
- ✅ Visualização de levantamentos topográficos
- ✅ Medição precisa de distâncias e áreas
- ✅ Análise de coordenadas em diferentes sistemas
- ✅ Geração de relatórios profissionais

### **Para Equipes de Engenharia**
- ✅ Gestão colaborativa de projetos
- ✅ Controle de versões de dados geográficos
- ✅ Interface web para trabalho remoto
- ✅ Integração com ferramentas CAD

### **Para Desenvolvedores**
- ✅ APIs REST para integração
- ✅ Arquitetura modular e extensível
- ✅ Documentação completa
- ✅ Sistema de plugins (futuro)

## 📊 **Dados Incluídos**

O sistema vem com dados reais pré-carregados:

| Camada | Features | Descrição |
|--------|----------|-----------|
| 🏗️ **Edifícios** | 23.193 | Polígonos de edificações |
| 🛣️ **Estradas** | 35.158 | Malha viária completa |
| 📍 **Lugares** | 670 | Pontos de interesse |
| 🗺️ **Setores** | 2.478 | Setores censitários |
| **Total** | **61.499** | **Features geográficas** |

## 🔐 **Segurança**

- ✅ **Sanitização de inputs** contra XSS
- ✅ **Validação de arquivos** rigorosa
- ✅ **Headers de segurança** implementados
- ✅ **Proteção contra path traversal**
- ✅ **Logs de auditoria** completos

## 🧪 **Testes**

```bash
# Executar testes completos
python3 tests/test_simple_server.py

# Verificar APIs
python3 tests/test_webserver.py
```

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 **Changelog**

### **v1.0.0** (Atual)
- ✅ Sistema web funcional completo
- ✅ 61.499 features geográficas importadas
- ✅ APIs REST implementadas
- ✅ Interface profissional para topógrafos
- ✅ Ferramentas de medição integradas

## 📄 **Licença**

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 **Autor**

**Anderson Math** - [@AndersonMathz](https://github.com/AndersonMathz)

## 🙏 **Agradecimentos**

- [Leaflet.js](https://leafletjs.com/) pela excelente biblioteca de mapas
- [Bootstrap](https://getbootstrap.com/) pelo framework CSS
- Comunidade de desenvolvedores GIS

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**

*Desenvolvido com ❤️ para a comunidade de topografia e engenharia*
