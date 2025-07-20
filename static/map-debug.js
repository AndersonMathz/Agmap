// Script de debug para o mapa
console.log('🔍 Debug: Script de debug carregado');

// Verificar se Leaflet está disponível
if (typeof L !== 'undefined') {
    console.log('✅ Leaflet está disponível, versão:', L.version);
} else {
    console.error('❌ Leaflet não está disponível');
}

// Aguardar DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Debug: DOM carregado');
    
    // Verificar elemento do mapa
    const mapElement = document.getElementById('map');
    if (mapElement) {
        console.log('✅ Elemento #map encontrado:', mapElement);
        console.log('Dimensões:', mapElement.offsetWidth, 'x', mapElement.offsetHeight);
    } else {
        console.error('❌ Elemento #map não encontrado');
    }
    
    // Tentar criar um mapa simples
    setTimeout(() => {
        try {
            if (mapElement && typeof L !== 'undefined') {
                console.log('🔍 Tentando criar mapa simples...');
                
                // Verificar se já existe um mapa
                if (window.map && typeof window.map.addLayer === 'function') {
                    console.log('✅ Mapa já existe e é válido');
                    return;
                }
                
                // Limpar elemento se houver conteúdo
                mapElement.innerHTML = '';
                
                const simpleMap = L.map('map', {
                    center: [-2.5, -44.3],
                    zoom: 10,
                    zoomControl: false
                });
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19
                }).addTo(simpleMap);
                
                // Controles de zoom removidos - usando toolbar customizada
                
                // Expor globalmente - IMPORTANTE: garantir que é o objeto Leaflet
                window.map = simpleMap;
                
                console.log('✅ Mapa criado com sucesso!');
                console.log('Tipo do mapa:', typeof window.map);
                console.log('Métodos disponíveis:', Object.getOwnPropertyNames(window.map.__proto__));
                
                // Forçar resize do mapa
                setTimeout(() => {
                    window.map.invalidateSize();
                }, 100);
                
                // Disparar evento personalizado para notificar que o mapa está pronto
                const mapReadyEvent = new CustomEvent('mapReady', { 
                    detail: { map: window.map } 
                });
                document.dispatchEvent(mapReadyEvent);
                console.log('📡 Evento mapReady disparado');
                
            } else {
                console.error('❌ Não foi possível criar mapa: elemento ou Leaflet não disponível');
            }
        } catch (error) {
            console.error('❌ Erro criando mapa simples:', error);
        }
    }, 500);
});