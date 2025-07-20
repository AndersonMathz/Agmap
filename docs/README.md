# WebGIS - Visualização de Dados Geográficos

Um sistema WebGIS moderno para visualização de dados geográficos em formato shapefile, desenvolvido com HTML5, CSS3 e JavaScript.

## 🚀 Funcionalidades

- **Mapas Base**: OpenStreetMap e Google Satélite
- **Camadas de Dados**: Visualização de múltiplos shapefiles
- **Interface Responsiva**: Design moderno e adaptável
- **Controles Interativos**: Zoom, pan, seleção de features
- **Informações Detalhadas**: Popups e painel de informações
- **Gerenciamento de Camadas**: Ativar/desativar camadas individualmente

## 📁 Estrutura do Projeto

```
WEBAG/
├── index.html          # Página principal
├── styles.css          # Estilos CSS
├── script.js           # Lógica JavaScript
├── README.md           # Este arquivo
├── test_files.html     # Página de teste
├── SOLUCAO_PROBLEMAS.md # Guia de solução de problemas
└── WEBGIS_ANDERSON/
    └── OSM_BLACK/      # Arquivos shapefile
        ├── __building_pl.shp
        ├── __road_ln.shp
        ├── __places_pt.shp
        ├── __MA_Setores_2021.shp
        └── ...
```

## 🛠️ Tecnologias Utilizadas

- **Leaflet.js**: Biblioteca para mapas interativos
- **Bootstrap 5**: Framework CSS para interface responsiva
- **Font Awesome**: Ícones
- **shpjs**: Biblioteca para carregar arquivos shapefile
- **HTML5/CSS3/JavaScript**: Tecnologias web padrão

## 🚀 Como Usar

### 1. Preparação

Certifique-se de que os arquivos shapefile estão na pasta `WEBGIS_ANDERSON/OSM_BLACK/` com a seguinte estrutura:
- `__building_pl.shp` (edifícios)
- `__road_ln.shp` (estradas)
- `__places_pt.shp` (lugares)
- `__MA_Setores_2021.shp` (setores censitários)

### 2. Execução

1. Abra o arquivo `index.html` em um navegador web moderno
2. Aguarde o carregamento dos dados geográficos
3. O mapa será automaticamente ajustado para a extensão dos dados

### 3. Navegação

- **Zoom**: Use os controles de zoom ou a roda do mouse
- **Pan**: Clique e arraste para mover o mapa
- **Seleção**: Clique em qualquer feature para selecioná-la
- **Informações**: Clique em features para ver detalhes no popup

## 🎛️ Controles da Interface

### Sidebar (Painel Lateral)

#### Mapas Base
- **OpenStreetMap**: Mapa base padrão
- **Google Satélite**: Imagem de satélite

#### Camadas de Dados
- **Edifícios**: Polígonos de edifícios (vermelho)
- **Estradas**: Linhas de estradas (azul claro)
- **Lugares**: Pontos de lugares (amarelo)
- **Setores Censitários**: Polígonos de setores censitários (verde claro)

#### Controles
- **Zoom para Extensão**: Ajusta o zoom para mostrar todos os dados
- **Limpar Seleção**: Remove a seleção atual

### Controles do Mapa
- **Zoom In/Out**: Botões de zoom
- **Tela Cheia**: Modo tela cheia

## 🔧 Personalização

### Cores das Camadas

Para alterar as cores das camadas, edite o arquivo `script.js` na seção `layerConfig`:

```javascript
const layerConfig = {
    buildings: {
        file: 'WEBGIS_ANDERSON/OSM_BLACK/building_pl.shp',
        color: '#ff6b6b',  // Altere esta cor
        weight: 1,
        opacity: 0.8,
        fillOpacity: 0.3
    },
    // ... outras camadas
};
```

### Adicionar Novas Camadas

Para adicionar uma nova camada:

1. Adicione a configuração em `layerConfig`
2. Adicione o checkbox no HTML
3. Certifique-se de que o arquivo shapefile existe

### Estilos CSS

O arquivo `styles.css` contém todos os estilos. Você pode personalizar:
- Cores do tema
- Layout da sidebar
- Estilos dos controles
- Responsividade

## 🌐 Requisitos do Sistema

- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexão com internet (para mapas base)
- Servidor web local (recomendado para melhor performance)

## 🔍 Solução de Problemas

### Dados não carregam
- Verifique se os arquivos shapefile estão na pasta correta
- Abra o console do navegador (F12) para ver erros
- Certifique-se de que está usando um servidor web local

### Mapa não aparece
- Verifique a conexão com internet
- Confirme se as bibliotecas estão carregando corretamente

### Performance lenta
- Considere usar arquivos shapefile menores
- Otimize os dados antes de carregar
- Use um servidor web local em vez de abrir diretamente o arquivo HTML

## 📝 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

## 🤝 Contribuições

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades.

---

**Desenvolvido para visualização de dados geográficos de localização** 