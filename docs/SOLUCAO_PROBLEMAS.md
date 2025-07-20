# 🔧 Solução de Problemas - WebGIS

## ❌ Problema: Arquivos não carregam no WebGIS

### 🔍 Diagnóstico

Se os arquivos shapefile não estão aparecendo no mapa, siga estes passos para diagnosticar:

#### 1. **Teste os Arquivos**
- Clique no botão **"Testar Arquivos"** na sidebar do WebGIS
- Ou acesse diretamente: `http://localhost:8000/test_files.html`
- Isso irá verificar se cada arquivo shapefile está acessível

#### 2. **Verifique o Console do Navegador**
- Pressione **F12** para abrir as ferramentas do desenvolvedor
- Vá para a aba **"Console"**
- Procure por mensagens de erro em vermelho
- As mensagens de debug em azul mostram o progresso do carregamento

#### 3. **Verifique a Estrutura de Pastas**
Certifique-se de que os arquivos estão na pasta correta:
```
WEBAG/
├── index.html
├── styles.css
├── script.js
├── test_files.html
├── SOLUCAO_PROBLEMAS.md
└── WEBGIS_ANDERSON/
    └── OSM_BLACK/
        ├── __building_pl.shp
        ├── __building_pl.dbf
        ├── __building_pl.shx
        ├── __road_ln.shp
        ├── __road_ln.dbf
        ├── __road_ln.shx
        ├── __places_pt.shp
        ├── __places_pt.dbf
        ├── __places_pt.shx
        ├── __MA_Setores_2021.shp
        ├── __MA_Setores_2021.dbf
        ├── __MA_Setores_2021.shx
        └── ... (outros arquivos)
```

### 🛠️ Soluções Comuns

#### **Problema 1: Biblioteca shpjs não carrega**
**Sintomas:** Erro "shp is not defined" no console

**Solução:**
1. Verifique sua conexão com a internet
2. Recarregue a página (F5)
3. Tente usar um navegador diferente

#### **Problema 2: Arquivos não encontrados**
**Sintomas:** Erro 404 ou "File not found"

**Solução:**
1. Certifique-se de que está usando o servidor Python
2. Execute: `python server.py`
3. Acesse: `http://localhost:8000`

#### **Problema 3: CORS (Cross-Origin Resource Sharing)**
**Sintomas:** Erro de CORS no console

**Solução:**
1. **NUNCA** abra o arquivo HTML diretamente no navegador
2. **SEMPRE** use o servidor Python
3. Execute: `python server.py`

#### **Problema 4: Arquivos shapefile corrompidos**
**Sintomas:** Erro ao processar shapefile

**Solução:**
1. Verifique se todos os arquivos (.shp, .dbf, .shx) estão presentes
2. Tente abrir os arquivos em um software GIS (QGIS, ArcGIS)
3. Se necessário, reconverta os arquivos

### 📋 Checklist de Verificação

- [ ] Servidor Python está rodando (`python server.py`)
- [ ] Acessando via `http://localhost:8000`
- [ ] Todos os arquivos shapefile estão na pasta correta
- [ ] Arquivos .shp, .dbf, .shx estão presentes
- [ ] Conexão com internet ativa
- [ ] Navegador atualizado (Chrome, Firefox, Edge)

### 🚀 Como Testar

1. **Inicie o servidor:**
   ```bash
   python server.py
   ```

2. **Abra o navegador:**
   ```
   http://localhost:8000
   ```

3. **Teste os arquivos:**
   - Clique em "Testar Arquivos" na sidebar
   - Verifique se todos os arquivos carregam

4. **Verifique o console:**
   - Pressione F12
   - Procure por mensagens de erro

### 📞 Se o Problema Persistir

Se após seguir todos os passos o problema persistir:

1. **Capture o erro:**
   - Tire um screenshot do console (F12)
   - Anote as mensagens de erro exatas

2. **Verifique os logs:**
   - O servidor Python mostra logs no terminal
   - Verifique se há erros 404 ou 500

3. **Teste arquivo por arquivo:**
   - Use a página de teste para verificar cada arquivo individualmente
   - Identifique qual arquivo específico está falhando

### 🔄 Alternativas

Se os shapefiles continuarem com problemas:

1. **Converta para GeoJSON:**
   - Use QGIS ou outra ferramenta para converter .shp para .geojson
   - Atualize o código para carregar .geojson diretamente

2. **Use arquivos menores:**
   - Divida arquivos grandes em partes menores
   - Remova dados desnecessários

3. **Servidor alternativo:**
   - Use um servidor web como Apache ou Nginx
   - Configure corretamente os headers CORS

---

**💡 Dica:** O problema mais comum é tentar abrir o arquivo HTML diretamente no navegador. **SEMPRE** use o servidor Python para evitar problemas de CORS. 