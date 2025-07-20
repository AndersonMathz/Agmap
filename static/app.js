// WebGIS App - Funcionalidades Gerais

// Verificar se o usuário está autenticado
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/check');
        if (!response.ok) {
            window.location.href = '/login';
            return false;
        }
        
        const data = await response.json();
        if (data.authenticated && data.user) {
            // Definir currentUser globalmente
            window.currentUser = data.user;
            console.log('✅ Usuário autenticado:', data.user.username, 'Role:', data.user.role);
            
            // Atualizar informações do usuário na interface
            updateUserInfo(data.user);
        }
        
        return true;
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = '/login';
        return false;
    }
}

// Atualizar informações do usuário na interface
function updateUserInfo(user) {
    const userInfoElement = document.getElementById('user-info');
    if (userInfoElement) {
        userInfoElement.textContent = `Bem-vindo, ${user.name}`;
    }
}

// Função de logout
function logout() {
    window.location.href = '/logout';
}

// ===== FUNÇÕES DE IMPORT/EXPORT =====

// Função para importar arquivo
function importFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.kml,.kmz,.geojson,.json';
    input.onchange = handleFileImport;
    input.click();
}

async function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    try {
        showNotification('Importando arquivo...', 'info');
        
        if (fileExtension === 'geojson' || fileExtension === 'json') {
            await importGeoJSON(file);
        } else if (fileExtension === 'kml' || fileExtension === 'kmz') {
            await importKML(file);
        } else {
            throw new Error('Formato de arquivo não suportado');
        }
        
        showNotification('Arquivo importado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro importando arquivo:', error);
        showNotification('Erro ao importar arquivo: ' + error.message, 'error');
    }
}

async function importGeoJSON(file) {
    const text = await file.text();
    const geojson = JSON.parse(text);
    
    if (geojson.type === 'FeatureCollection') {
        for (const feature of geojson.features) {
            await addFeatureToMap(feature);
        }
        // Atualizar lista de camadas uma vez após todas as importações
        if (window.GeoJsonTools) {
            window.GeoJsonTools.updateLayersList();
        }
    } else if (geojson.type === 'Feature') {
        await addFeatureToMap(geojson);
        // Atualizar lista de camadas
        if (window.GeoJsonTools) {
            window.GeoJsonTools.updateLayersList();
        }
    } else {
        throw new Error('Formato GeoJSON inválido');
    }
}

async function importKML(file) {
    const text = await file.text();
    
    // Usar toGeoJSON para converter KML para GeoJSON
    const parser = new DOMParser();
    const kmlDoc = parser.parseFromString(text, 'text/xml');
    const geojson = toGeoJSON.kml(kmlDoc);
    
    if (geojson.features && geojson.features.length > 0) {
        for (const feature of geojson.features) {
            await addFeatureToMap(feature);
        }
        // Atualizar lista de camadas uma vez após todas as importações KML
        if (window.GeoJsonTools) {
            window.GeoJsonTools.updateLayersList();
        }
    } else {
        throw new Error('Nenhuma feature encontrada no arquivo KML');
    }
}

async function addFeatureToMap(feature) {
    try {
        // Criar layer do Leaflet baseado na geometria
        let layer;
        const geometry = feature.geometry;
        const properties = feature.properties || {};
        
        switch (geometry.type) {
            case 'Point':
                layer = L.marker([geometry.coordinates[1], geometry.coordinates[0]]);
                break;
            case 'LineString':
                layer = L.polyline(geometry.coordinates.map(coord => [coord[1], coord[0]]));
                break;
            case 'Polygon':
                layer = L.polygon(geometry.coordinates[0].map(coord => [coord[1], coord[0]]));
                break;
            default:
                console.warn('Tipo de geometria não suportado:', geometry.type);
                return;
        }
        
        // Gerar ID único se não existir
        if (!layer._featureId) {
            layer._featureId = 'imported_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        // Adicionar propriedades
        layer.feature = feature;
        
        // Adicionar ao mapa
        if (window.drawnItems && typeof window.drawnItems.addLayer === 'function') {
            window.drawnItems.addLayer(layer);
        } else if (window.map && typeof layer.addTo === 'function') {
            layer.addTo(window.map);
        }
        
        // Salvar feature importada no banco de dados
        if (window.GeoJsonTools && window.GeoJsonTools.saveFeatureToDatabase) {
            await window.GeoJsonTools.saveFeatureToDatabase(layer);
            console.log('✅ Feature importada salva no banco:', layer._featureId);
        } else {
            console.warn('⚠️ Não foi possível adicionar layer ao mapa - mapa ou drawnItems não disponível');
        }
        
        // Configurar evento de clique
        layer.on('click', function() {
            if (window.GeoJsonTools) {
                window.currentFeature = layer;
                window.openAttributeModal(layer);
            }
        });
        
        // Salvar no banco
        if (window.GeoJsonTools) {
            await window.GeoJsonTools.saveFeatureToDatabase(layer);
        }
        
    } catch (error) {
        console.error('Erro adicionando feature ao mapa:', error);
        throw error;
    }
}

// Função para exportar dados
function exportData(format) {
    switch (format) {
        case 'geojson':
            exportGeoJSON();
            break;
        case 'kml':
            exportKML();
            break;
        case 'shapefile':
            exportShapefile();
            break;
        default:
            showNotification('Formato de exportação não suportado', 'error');
    }
}

function exportGeoJSON() {
    try {
        if (window.GeoJsonTools) {
            window.GeoJsonTools.downloadGeoJSON();
        } else {
            showNotification('Sistema de exportação não disponível', 'error');
        }
    } catch (error) {
        console.error('Erro exportando GeoJSON:', error);
        showNotification('Erro ao exportar GeoJSON', 'error');
    }
}

function exportKML() {
    try {
        // Implementar exportação KML
        const features = window.GeoJsonTools ? window.GeoJsonTools.exportAllFeatures() : null;
        if (!features || features.features.length === 0) {
            showNotification('Nenhuma feature para exportar', 'warning');
            return;
        }
        
        // Converter GeoJSON para KML (implementação simplificada)
        const kml = convertGeoJSONToKML(features);
        
        const blob = new Blob([kml], { type: 'application/vnd.google-earth.kml+xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'features_' + new Date().toISOString().split('T')[0] + '.kml';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification('KML exportado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro exportando KML:', error);
        showNotification('Erro ao exportar KML', 'error');
    }
}

function exportShapefile() {
    showNotification('Exportação Shapefile será implementada em versão futura', 'info');
}

function convertGeoJSONToKML(geojson) {
    let kml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n';
    kml += '<Document>\n';
    kml += '<name>WebGIS Export</name>\n';
    
    geojson.features.forEach((feature, index) => {
        kml += '<Placemark>\n';
        kml += `<name>Feature ${index + 1}</name>\n`;
        
        // Adicionar propriedades como descrição
        if (feature.properties && Object.keys(feature.properties).length > 0) {
            kml += '<description><![CDATA[\n';
            Object.entries(feature.properties).forEach(([key, value]) => {
                kml += `<strong>${key}:</strong> ${value}<br>\n`;
            });
            kml += ']]></description>\n';
        }
        
        // Adicionar geometria
        const geometry = feature.geometry;
        switch (geometry.type) {
            case 'Point':
                kml += '<Point>\n';
                kml += `<coordinates>${geometry.coordinates[0]},${geometry.coordinates[1]},0</coordinates>\n`;
                kml += '</Point>\n';
                break;
            case 'LineString':
                kml += '<LineString>\n';
                kml += '<coordinates>\n';
                geometry.coordinates.forEach(coord => {
                    kml += `${coord[0]},${coord[1]},0 `;
                });
                kml += '\n</coordinates>\n';
                kml += '</LineString>\n';
                break;
            case 'Polygon':
                kml += '<Polygon>\n';
                kml += '<outerBoundaryIs>\n';
                kml += '<LinearRing>\n';
                kml += '<coordinates>\n';
                geometry.coordinates[0].forEach(coord => {
                    kml += `${coord[0]},${coord[1]},0 `;
                });
                kml += '\n</coordinates>\n';
                kml += '</LinearRing>\n';
                kml += '</outerBoundaryIs>\n';
                kml += '</Polygon>\n';
                break;
        }
        
        kml += '</Placemark>\n';
    });
    
    kml += '</Document>\n';
    kml += '</kml>';
    
    return kml;
}

// Sanitizar entrada do usuário
function sanitizeInput(input) {
    if (!input) return '';
    return input.toString().replace(/[<>'"]/g, '');
}

// Mostrar notificação
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    
    // Definir classe e ícone baseado no tipo
    let notificationClass = 'success-notification';
    let icon = 'fas fa-check-circle';
    
    if (type === 'error') {
        notificationClass = 'error-notification';
        icon = 'fas fa-exclamation-circle';
    } else if (type === 'warning') {
        notificationClass = 'warning-notification'; 
        icon = 'fas fa-exclamation-triangle';
    } else if (type === 'info') {
        notificationClass = 'info-notification';
        icon = 'fas fa-info-circle';
    }
    
    notification.className = notificationClass;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 4 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 4000);
}

// Verificar se é HTTPS
function isSecureConnection() {
    return window.location.protocol === 'https:';
}

// Mostrar aviso se não for HTTPS
if (!isSecureConnection() && window.location.hostname !== 'localhost') {
    showNotification('Este site deve ser acessado via HTTPS para maior segurança.', 'warning');
}

// Inicialização geral
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 WebGIS App inicializado');
    
    // Verificar autenticação apenas se não estiver na página de login ou debug
    if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/debug')) {
        console.log('🔍 Verificando autenticação...');
        checkAuthStatus();
    } else {
        console.log('⏭️ Pulando verificação de autenticação para esta página');
    }
}); 