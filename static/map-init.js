/**
 * Inicializador robusto do mapa WebGIS
 * Garante que o mapa seja criado corretamente e todas as dependências estejam disponíveis
 */

// Variáveis globais
window.webgisReady = false;
window.mapInitAttempts = 0;
window.maxInitAttempts = 10;

// Função principal de inicialização
function initWebGISMap() {
    window.mapInitAttempts++;
    
    console.log(`🚀 Tentativa ${window.mapInitAttempts} de inicialização do WebGIS`);
    
    // Verificar se já foi inicializado
    if (window.webgisReady) {
        console.log('✅ WebGIS já inicializado');
        return true;
    }
    
    // Verificar se excedeu tentativas máximas
    if (window.mapInitAttempts > window.maxInitAttempts) {
        console.error('❌ Número máximo de tentativas de inicialização excedido');
        return false;
    }
    
    // Verificar dependências
    if (!checkDependencies()) {
        setTimeout(initWebGISMap, 300);
        return false;
    }
    
    // Verificar elemento do mapa
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('❌ Elemento #map não encontrado');
        setTimeout(initWebGISMap, 300);
        return false;
    }
    
    // Verificar se o mapa já existe
    if (window.map && window.map._container) {
        console.log('✅ Mapa já existe, configurando variáveis globais');
        setupGlobalVariables();
        return true;
    }
    
    // Criar novo mapa
    try {
        createNewMap();
        return true;
    } catch (error) {
        console.error('❌ Erro ao criar mapa:', error);
        setTimeout(initWebGISMap, 500);
        return false;
    }
}

// Verificar dependências necessárias
function checkDependencies() {
    if (typeof L === 'undefined') {
        console.log('⏳ Aguardando Leaflet carregar...');
        return false;
    }
    
    if (typeof L.map !== 'function') {
        console.log('⏳ Leaflet ainda não está completamente carregado...');
        return false;
    }
    
    return true;
}

// Criar novo mapa
function createNewMap() {
    console.log('🗺️ Criando novo mapa...');
    
    const mapElement = document.getElementById('map');
    
    // Limpar elemento do mapa
    mapElement.innerHTML = '';
    
    // Configurações do mapa
    const mapOptions = {
        center: [-2.5297, -44.3028], // São Luís, MA
        zoom: 13,
        zoomControl: false,
        attributionControl: true,
        maxZoom: 19,
        minZoom: 3
    };
    
    // Criar mapa
    window.map = L.map('map', mapOptions);
    
    // Adicionar camada base
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        crossOrigin: true
    });
    
    osmLayer.addTo(window.map);
    
    // Configurar variáveis globais
    setupGlobalVariables();
    
    // Forçar redimensionamento
    setTimeout(() => {
        if (window.map) {
            window.map.invalidateSize();
            console.log('🔄 Tamanho do mapa invalidado');
        }
    }, 200);
    
    console.log('✅ Mapa criado com sucesso');
}

// Configurar variáveis globais
function setupGlobalVariables() {
    // Criar grupo de elementos desenhados se não existir
    if (!window.drawnItems) {
        window.drawnItems = new L.FeatureGroup();
        window.map.addLayer(window.drawnItems);
        console.log('✅ DrawnItems criado');
    }
    
    // Marcar como pronto
    window.webgisReady = true;
    
    // Disparar eventos
    dispatchMapEvents();
}

// Disparar eventos para outros scripts
function dispatchMapEvents() {
    console.log('📡 Disparando eventos do mapa...');
    
    // Evento mapReady
    document.dispatchEvent(new CustomEvent('mapReady', {
        detail: { 
            map: window.map, 
            drawnItems: window.drawnItems 
        }
    }));
    
    // Evento webgisReady
    document.dispatchEvent(new CustomEvent('webgisReady', {
        detail: { 
            map: window.map, 
            drawnItems: window.drawnItems,
            ready: true
        }
    }));
    
    console.log('✅ Eventos disparados');
}

// Auto-inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 DOM carregado, iniciando WebGIS...');
    setTimeout(initWebGISMap, 100);
});

// Fallback adicional
setTimeout(function() {
    if (!window.webgisReady) {
        console.log('🔄 Fallback: tentando inicializar WebGIS...');
        initWebGISMap();
    }
}, 1000);

// Exportar função para uso manual
window.initWebGISMap = initWebGISMap;