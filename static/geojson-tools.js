/**
 * Ferramentas estilo GeoJSON.io para WebGIS
 * Implementa funcionalidades de desenho, edição e gerenciamento de atributos
 */

// Variáveis globais
let currentTool = 'pan';
let drawControl = null;
let editControl = null;
let currentFeature = null;
let drawnItems = new L.FeatureGroup();
let featureCounter = 0;
let isInitialized = false;

// Inicializar ferramentas quando mapa estiver pronto
document.addEventListener('mapReady', function(event) {
    console.log('📡 Evento mapReady recebido, inicializando GeoJSON Tools...');
    initializeGeoJsonTools();
});

// Fallback: aguardar DOM + timeout
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM carregado, aguardando mapa...');
    
    // Aguardar o mapa estar disponível (fallback)
    setTimeout(() => {
        if (window.map && typeof window.map.addLayer === 'function') {
            console.log('⏰ Fallback: mapa encontrado após timeout');
            initializeGeoJsonTools();
        } else {
            console.log('⏳ Aguardando evento mapReady...');
        }
    }, 2000);
});

function initializeGeoJsonTools() {
    if (isInitialized) {
        console.log('⚠️ GeoJSON Tools já foram inicializadas');
        return;
    }

    if (!window.map) {
        console.error('Mapa não está disponível');
        return;
    }

    console.log('🔧 Inicializando GeoJSON Tools...');

    // Verificar se map tem método addLayer
    if (typeof window.map.addLayer !== 'function') {
        console.error('❌ window.map.addLayer não é uma função:', typeof window.map.addLayer);
        console.log('window.map:', window.map);
        return;
    }

    // Adicionar FeatureGroup ao mapa
    window.map.addLayer(drawnItems);
    
    // Configurar controles de desenho
    setupDrawControls();
    
    // Configurar event listeners da toolbar
    setupToolbarEvents();
    
    // Configurar modal de atributos
    setupAttributeModal();
    
    // Configurar eventos do mapa
    setupMapEvents();
    
    // Carregar features existentes do banco com delay
    setTimeout(() => {
        loadExistingFeatures();
    }, 2000);
    
    // Adicionar recarregamento das features quando a página ganha foco
    window.addEventListener('focus', () => {
        console.log('🔄 Página ganhou foco, recarregando features...');
        setTimeout(() => {
            loadExistingFeatures();
        }, 500);
    });
    
    // Expor variáveis globalmente
    window.drawnItems = drawnItems;
    window.currentFeature = currentFeature;
    window.openAttributeModal = openAttributeModal;
    window.loadExistingFeatures = loadExistingFeatures; // Expor para debug
    
    // Aplicar máscaras de campos na inicialização
    setTimeout(() => {
        setupFieldMasks();
    }, 500);
    
    // Marcar como inicializado
    isInitialized = true;
    
    console.log('✅ GeoJSON.io tools inicializadas com sucesso!');
}

function setupDrawControls() {
    // Remover controles existentes se houver
    if (drawControl) {
        window.map.removeControl(drawControl);
        drawControl = null;
    }
    
    // NÃO adicionar controles do Leaflet Draw - usando apenas nossa toolbar customizada
    console.log('✅ Draw controls configurados - usando apenas toolbar customizada');
}

function setupToolbarEvents() {
    // Zoom controls
    document.getElementById('zoom-in-btn').addEventListener('click', function() {
        window.map.zoomIn();
    });
    
    document.getElementById('zoom-out-btn').addEventListener('click', function() {
        window.map.zoomOut();
    });
    
    // Pan control
    document.getElementById('pan-btn').addEventListener('click', function() {
        setActiveTool('pan');
    });
    
    // Locate control
    document.getElementById('locate-btn').addEventListener('click', function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                window.map.setView([lat, lng], 15);
                
                L.marker([lat, lng]).addTo(window.map)
                    .bindPopup('Você está aqui!')
                    .openPopup();
            }, function(error) {
                alert('Erro ao obter localização: ' + error.message);
            });
        } else {
            alert('Geolocalização não suportada pelo navegador');
        }
    });
    
    // Drawing tools
    document.getElementById('draw-point-btn').addEventListener('click', function() {
        setActiveTool('draw-point');
        startDrawing('marker');
    });
    
    document.getElementById('draw-line-btn').addEventListener('click', function() {
        setActiveTool('draw-line');
        startDrawing('polyline');
    });
    
    document.getElementById('draw-polygon-btn').addEventListener('click', function() {
        setActiveTool('draw-polygon');
        startDrawing('polygon');
    });
    
    // Edit tools
    document.getElementById('edit-btn').addEventListener('click', function() {
        setActiveTool('edit');
        startEditing();
    });
    
    document.getElementById('delete-btn').addEventListener('click', function() {
        setActiveTool('delete');
        startDeleting();
    });
    
    // Shape tools
    document.getElementById('rectangle-btn').addEventListener('click', function() {
        setActiveTool('rectangle');
        startDrawing('rectangle');
    });
    
    document.getElementById('circle-btn').addEventListener('click', function() {
        setActiveTool('circle');
        startDrawing('circle');
    });
    
    // Settings
    document.getElementById('settings-btn').addEventListener('click', function() {
        alert('Configurações em desenvolvimento');
    });
}

function setActiveTool(tool) {
    // Remover classe active de todos os botões
    document.querySelectorAll('.geojson-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Adicionar classe active ao botão atual
    const btn = document.getElementById(tool + '-btn');
    if (btn) {
        btn.classList.add('active');
    }
    
    currentTool = tool;
    
    // Habilitar/desabilitar interações do mapa
    if (tool === 'pan') {
        window.map.dragging.enable();
        window.map.doubleClickZoom.enable();
        window.map.scrollWheelZoom.enable();
    }
}

function startDrawing(type) {
    // Disable map interactions while drawing
    window.map.dragging.disable();
    window.map.doubleClickZoom.disable();
    
    let drawHandler;
    
    // Configurações de estilo padrão
    const defaultStyles = {
        color: '#2e60ff',
        weight: 3,
        fillColor: '#2e60ff',
        fillOpacity: 0.3
    };
    
    const markerIcon = new L.Icon({
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    switch(type) {
        case 'marker':
            drawHandler = new L.Draw.Marker(window.map, { icon: markerIcon });
            break;
        case 'polyline':
            drawHandler = new L.Draw.Polyline(window.map, { shapeOptions: defaultStyles });
            break;
        case 'polygon':
            drawHandler = new L.Draw.Polygon(window.map, { 
                allowIntersection: false,
                shapeOptions: defaultStyles 
            });
            break;
        case 'rectangle':
            drawHandler = new L.Draw.Rectangle(window.map, { shapeOptions: defaultStyles });
            break;
        case 'circle':
            drawHandler = new L.Draw.Circle(window.map, { shapeOptions: defaultStyles });
            break;
    }
    
    if (drawHandler) {
        drawHandler.enable();
    }
}

function startEditing() {
    if (drawnItems.getLayers().length === 0) {
        alert('Nenhuma feature para editar');
        setActiveTool('pan');
        return;
    }
    
    const editHandler = new L.EditToolbar.Edit(window.map, {
        featureGroup: drawnItems
    });
    editHandler.enable();
}

function startDeleting() {
    if (drawnItems.getLayers().length === 0) {
        alert('Nenhuma feature para deletar');
        setActiveTool('pan');
        return;
    }
    
    const deleteHandler = new L.EditToolbar.Delete(window.map, {
        featureGroup: drawnItems
    });
    deleteHandler.enable();
}

function setupMapEvents() {
    // Evento quando uma feature é criada
    window.map.on('draw:created', function (e) {
        const layer = e.layer;
        featureCounter++;
        
        // Adicionar ID único
        layer._featureId = 'feature_' + Date.now() + '_' + featureCounter;
        
        // Adicionar ao grupo de features
        drawnItems.addLayer(layer);
        
        // Configurar evento de clique para edição de atributos
        layer.on('click', function() {
            currentFeature = layer;
            openAttributeModal(layer);
        });
        
        // Salvar imediatamente no banco de dados
        saveFeatureToDatabase(layer);
        
        // Auto-abrir modal de atributos para novas features
        currentFeature = layer;
        openAttributeModal(layer);
        
        // Voltar para modo pan
        setActiveTool('pan');
        
        // Re-habilitar interações do mapa
        window.map.dragging.enable();
        window.map.doubleClickZoom.enable();
        
        console.log('✅ Nova feature criada e salva:', layer._featureId);
    });
    
    // Evento quando features são editadas
    window.map.on('draw:edited', function (e) {
        const layers = e.layers;
        layers.eachLayer(function (layer) {
            updateFeatureInfo(layer);
            // Salvar alterações no banco
            saveFeatureToDatabase(layer);
        });
        console.log('✅ Features editadas e salvas no banco');
    });
    
    // Evento quando features são deletadas
    window.map.on('draw:deleted', function (e) {
        const layers = e.layers;
        let count = 0;
        layers.eachLayer(function (layer) {
            // Deletar do banco de dados
            deleteFeatureFromDatabase(layer);
            count++;
        });
        console.log(`✅ ${count} feature(s) deletada(s) do banco`);
    });
    
    // Evento quando desenho é cancelado
    window.map.on('draw:drawstop', function (e) {
        setActiveTool('pan');
        window.map.dragging.enable();
        window.map.doubleClickZoom.enable();
    });
}

function setupAttributeModal() {
    // Event listeners do geojson-modal
    const closeBtn = document.getElementById('geojson-modal-close');
    const cancelBtn = document.getElementById('cancel-feature-btn');
    const saveBtn = document.getElementById('save-feature-btn');
    const deleteBtn = document.getElementById('delete-feature-btn');
    
    if (closeBtn) closeBtn.addEventListener('click', closeGeojsonModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeGeojsonModal);
    if (saveBtn) saveBtn.addEventListener('click', saveGeojsonAttributes);
    if (deleteBtn) deleteBtn.addEventListener('click', deleteCurrentFeature);
    
    // Tabs do modal
    const tabs = document.querySelectorAll('.geojson-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            switchGeojsonTab(this.dataset.tab);
        });
    });
    
    // Máscaras para campos
    setupFieldMasks();
}

function openAttributeModal(layer) {
    currentFeature = layer;
    
    // Usar o geojson-modal que é o mais completo
    const modal = document.getElementById('geojson-modal');
    
    if (!modal) {
        console.error('Geojson modal not found');
        return;
    }
    
    // Obter propriedades existentes
    const properties = layer.feature ? layer.feature.properties || {} : {};
    
    // Preencher formulário com dados existentes
    populateGeojsonForm(properties);
    
    // Calcular área e perímetro automaticamente
    calculateGeometry(layer);
    
    // Atualizar aba Info
    updateGeojsonInfoTab(layer);
    
    // Mostrar modal
    modal.style.display = 'flex';
    modal.style.zIndex = '10001';
    
    // Aplicar máscaras após o modal estar completamente visível
    setTimeout(() => {
        setupFieldMasks();
        console.log('Máscaras aplicadas aos campos');
    }, 200);
    
    console.log('Modal aberto para feature:', layer._featureId);
}

// ===== FUNÇÕES PARA GEOJSON MODAL =====

function populateGeojsonForm(properties) {
    // Informações da Gleba
    const glebaNumero = document.getElementById('gleba-numero');
    const glebaNome = document.getElementById('gleba-nome');
    const glebaArea = document.getElementById('gleba-area');
    const glebaPerimetro = document.getElementById('gleba-perimetro');
    
    if (glebaNumero) glebaNumero.value = properties.no_gleba || '';
    if (glebaNome) glebaNome.value = properties.nome_gleba || '';
    if (glebaArea) glebaArea.value = properties.area || '';
    if (glebaPerimetro) glebaPerimetro.value = properties.perimetro || '';
    
    // Informações do Proprietário
    const proprietarioNome = document.getElementById('proprietario-nome');
    const proprietarioCpf = document.getElementById('proprietario-cpf');
    const proprietarioRg = document.getElementById('proprietario-rg');
    
    if (proprietarioNome) proprietarioNome.value = properties.proprietario || '';
    if (proprietarioCpf) proprietarioCpf.value = properties.cpf || '';
    if (proprietarioRg) proprietarioRg.value = properties.rg || '';
    
    // Endereço
    const enderecoRua = document.getElementById('endereco-rua');
    const enderecoBairro = document.getElementById('endereco-bairro');
    const enderecoQuadra = document.getElementById('endereco-quadra');
    const enderecoCep = document.getElementById('endereco-cep');
    const enderecoCidade = document.getElementById('endereco-cidade');
    const enderecoUf = document.getElementById('endereco-uf');
    
    if (enderecoRua) enderecoRua.value = properties.rua || '';
    if (enderecoBairro) enderecoBairro.value = properties.bairro || '';
    if (enderecoQuadra) enderecoQuadra.value = properties.quadra || '';
    if (enderecoCep) enderecoCep.value = properties.cep || '';
    if (enderecoCidade) enderecoCidade.value = properties.cidade || '';
    if (enderecoUf) enderecoUf.value = properties.uf || '';
    
    // Testadas
    const testadaFrente = document.getElementById('testada-frente');
    const testadaLd = document.getElementById('testada-ld');
    const testadaLe = document.getElementById('testada-le');
    const testadaF = document.getElementById('testada-f');
    
    if (testadaFrente) testadaFrente.value = properties.testada_frente || '';
    if (testadaLd) testadaLd.value = properties.testada_ld || '';
    if (testadaLe) testadaLe.value = properties.testada_le || '';
    if (testadaF) testadaF.value = properties.testada_f || '';
    
    // Informações do Imóvel
    const imovelMatricula = document.getElementById('imovel-matricula');
    const zoneamento = document.getElementById('zoneamento');
    const finalidade = document.getElementById('finalidade');
    const padraoConstrutivo = document.getElementById('padrao-construtivo');
    const situacaoFundiaria = document.getElementById('situacao-fundiaria');
    const ocupacaoAtual = document.getElementById('ocupacao-atual');
    const descricaoImovel = document.getElementById('descricao-imovel');
    
    if (imovelMatricula) imovelMatricula.value = properties.matricula || '';
    if (zoneamento) zoneamento.value = properties.zoneamento || '';
    if (finalidade) finalidade.value = properties.finalidade || '';
    if (padraoConstrutivo) padraoConstrutivo.value = properties.padrao_construtivo || '';
    if (situacaoFundiaria) situacaoFundiaria.value = properties.situacao_fundiaria || '';
    if (ocupacaoAtual) ocupacaoAtual.value = properties.ocupacao_atual || '';
    if (descricaoImovel) descricaoImovel.value = properties.descricao_imovel || '';
}

function updateGeojsonInfoTab(layer) {
    // Atualizar informações técnicas
    const featureTypeInfo = document.getElementById('feature-type-info');
    const featureAreaInfo = document.getElementById('feature-area-info');
    const featureLengthInfo = document.getElementById('feature-length-info');
    const featureCoordsInfo = document.getElementById('feature-coords-info');
    
    if (featureTypeInfo) {
        let type = 'Desconhecido';
        if (layer.feature && layer.feature.geometry) {
            type = layer.feature.geometry.type;
            if (type === 'Polygon') type = 'Polígono';
            else if (type === 'LineString') type = 'Linha';
            else if (type === 'Point') type = 'Ponto';
        }
        featureTypeInfo.textContent = type;
    }
    
    if (featureAreaInfo && layer.feature && layer.feature.properties) {
        featureAreaInfo.textContent = layer.feature.properties.area ? 
            `${layer.feature.properties.area} m²` : 'Não calculado';
    }
    
    if (featureLengthInfo && layer.feature && layer.feature.properties) {
        featureLengthInfo.textContent = layer.feature.properties.perimetro ? 
            `${layer.feature.properties.perimetro} m` : 'Não calculado';
    }
    
    if (featureCoordsInfo && layer.feature && layer.feature.geometry) {
        const coords = JSON.stringify(layer.feature.geometry.coordinates).substring(0, 100) + '...';
        featureCoordsInfo.textContent = coords;
    }
}

function switchGeojsonTab(tabName) {
    // Atualizar tabs
    document.querySelectorAll('.geojson-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.geojson-tab[data-tab="${tabName}"]`).classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.geojson-tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(tabName + '-tab-content').classList.add('active');
}

// Manter compatibilidade com código antigo
function switchModalTab(tab) {
    // Atualizar tabs
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    const tabElement = document.getElementById(tab + '-tab');
    if (tabElement) tabElement.classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const contentElement = document.getElementById(tab + '-content');
    if (contentElement) contentElement.classList.add('active');
}

// ===== FUNÇÕES DE MÁSCARA =====
function setupFieldMasks() {
    // Função para aplicar máscara de CPF (000.000.000-00)
    function applyCpfMask(field) {
        if (field && !field.hasAttribute('data-mask-applied')) {
            field.setAttribute('data-mask-applied', 'true');
            field.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                }
                e.target.value = value;
            });
            console.log('Máscara CPF aplicada ao campo:', field.id);
        }
    }
    
    // Função para aplicar máscara de RG (000000000000-0)
    function applyRgMask(field) {
        if (field && !field.hasAttribute('data-mask-applied')) {
            field.setAttribute('data-mask-applied', 'true');
            field.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 13) {
                    value = value.replace(/(\d{12})(\d)/, '$1-$2');
                }
                e.target.value = value;
            });
            console.log('Máscara RG aplicada ao campo:', field.id);
        }
    }
    
    // Função para aplicar máscara de CEP (00000-000)
    function applyCepMask(field) {
        if (field && !field.hasAttribute('data-mask-applied')) {
            field.setAttribute('data-mask-applied', 'true');
            field.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 8) {
                    value = value.replace(/(\d{5})(\d)/, '$1-$2');
                }
                e.target.value = value;
            });
            console.log('Máscara CEP aplicada ao campo:', field.id);
        }
    }
    
    // Aplicar máscaras para campos do modal antigo
    applyCpfMask(document.getElementById('cpf'));
    applyRgMask(document.getElementById('rg'));
    applyCepMask(document.getElementById('cep'));
    
    // Aplicar máscaras para campos do geojson-modal
    applyCpfMask(document.getElementById('proprietario-cpf'));
    applyRgMask(document.getElementById('proprietario-rg'));
    applyCepMask(document.getElementById('endereco-cep'));
}

function populateGlebaForm(properties) {
    // Verificar se o formulário existe
    const form = document.getElementById('gleba-attributes-form');
    if (!form) {
        console.error('Formulário gleba-attributes-form não encontrado');
        return;
    }
    
    // Limpar formulário
    form.reset();
    
    // Preencher campos se houver dados
    const fields = [
        'no_gleba', 'nome_gleba', 'area', 'perimetro',
        'proprietario', 'cpf', 'rg',
        'rua', 'bairro', 'quadra', 'cep', 'cidade', 'uf',
        'testada_frente', 'testada_ld', 'testada_le', 'testada_f',
        'matricula', 'classe_imovel', 'tipo_imovel', 'descricao_imovel'
    ];
    
    fields.forEach(field => {
        const element = document.getElementById(field);
        if (element && properties[field]) {
            element.value = properties[field];
        }
    });
}

function calculateGeometry(layer) {
    const geom = layer.toGeoJSON();
    
    // Verificar se os campos existem
    const areaField = document.getElementById('area');
    const perimetroField = document.getElementById('perimetro');
    const distanciaField = document.getElementById('distancia');
    const areaFieldContainer = document.getElementById('area-field');
    const perimetroFieldContainer = document.getElementById('perimetro-field');
    const distanciaFieldContainer = document.getElementById('distancia-field');
    
    if (!areaField && !perimetroField && !distanciaField) {
        console.warn('Campos de geometria não encontrados');
        return;
    }
    
    // Mostrar/ocultar campos baseado no tipo de geometria
    if (geom.geometry.type === 'LineString') {
        // Para linhas: mostrar apenas distância
        if (areaFieldContainer) areaFieldContainer.style.display = 'none';
        if (perimetroFieldContainer) perimetroFieldContainer.style.display = 'none';
        if (distanciaFieldContainer) distanciaFieldContainer.style.display = 'block';
    } else {
        // Para polígonos/círculos: mostrar área e perímetro
        if (areaFieldContainer) areaFieldContainer.style.display = 'block';
        if (perimetroFieldContainer) perimetroFieldContainer.style.display = 'block';
        if (distanciaFieldContainer) distanciaFieldContainer.style.display = 'none';
    }
    
    try {
        if (geom.geometry.type === 'Polygon') {
            // Verificar se a biblioteca GeometryUtil está disponível
            if (typeof L.GeometryUtil !== 'undefined' && L.GeometryUtil.geodesicArea) {
                try {
                    const area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
                    areaField.value = area.toFixed(2);
                } catch (e) {
                    console.warn('Erro com L.GeometryUtil, usando cálculo alternativo');
                    // Cálculo alternativo simples
                    const coords = layer.getLatLngs()[0];
                    let area = 0;
                    for (let i = 0; i < coords.length; i++) {
                        const j = (i + 1) % coords.length;
                        area += coords[i].lat * coords[j].lng;
                        area -= coords[j].lat * coords[i].lng;
                    }
                    area = Math.abs(area) / 2;
                    // Converter de graus para metros aproximadamente (muito aproximado)
                    area = area * 111319.5 * 111319.5;
                    areaField.value = area.toFixed(2);
                }
            } else {
                // Método alternativo usando turf.js se disponível ou cálculo simples
                const coords = layer.getLatLngs()[0];
                let area = 0;
                for (let i = 0; i < coords.length; i++) {
                    const j = (i + 1) % coords.length;
                    area += coords[i].lat * coords[j].lng;
                    area -= coords[j].lat * coords[i].lng;
                }
                area = Math.abs(area) / 2;
                // Converter aproximadamente para metros²
                area = area * 111319.5 * 111319.5;
                areaField.value = area.toFixed(2);
            }
            
            // Calcular perímetro
            let perimeter = 0;
            const coords = layer.getLatLngs()[0];
            for (let i = 0; i < coords.length; i++) {
                const nextIndex = (i + 1) % coords.length;
                perimeter += coords[i].distanceTo(coords[nextIndex]);
            }
            perimetroField.value = perimeter.toFixed(2);
            
        } else if (geom.geometry.type === 'Circle') {
            const radius = layer.getRadius();
            const area = Math.PI * radius * radius;
            const perimeter = 2 * Math.PI * radius;
            
            areaField.value = area.toFixed(2);
            perimetroField.value = perimeter.toFixed(2);
        } else if (geom.geometry.type === 'LineString') {
            // Para linhas, calcular apenas comprimento
            let length = 0;
            const coords = layer.getLatLngs();
            for (let i = 0; i < coords.length - 1; i++) {
                length += coords[i].distanceTo(coords[i + 1]);
            }
            if (distanciaField) {
                distanciaField.value = length.toFixed(2);
            }
        } else {
            areaField.value = 'N/A';
            perimetroField.value = 'N/A';
        }
    } catch (error) {
        console.error('Erro calculando geometria:', error);
        if (areaField) areaField.value = 'Erro no cálculo';
        if (perimetroField) perimetroField.value = 'Erro no cálculo';
        if (distanciaField) distanciaField.value = 'Erro no cálculo';
    }
}

function updateInfoTab(layer) {
    const geom = layer.toGeoJSON();
    
    // Tipo de feature
    document.getElementById('feature-type').textContent = geom.geometry.type;
    
    // Data de criação (simular)
    document.getElementById('feature-created').textContent = new Date().toLocaleDateString();
    
    // Coordenadas
    let coords = 'N/A';
    if (geom.geometry.type === 'Point') {
        coords = `${geom.geometry.coordinates[1].toFixed(6)}, ${geom.geometry.coordinates[0].toFixed(6)}`;
    } else if (geom.geometry.coordinates && geom.geometry.coordinates[0]) {
        coords = `${geom.geometry.coordinates[0].length} pontos`;
    }
    document.getElementById('feature-coords').textContent = coords;
    
    // ID da feature
    document.getElementById('feature-id').textContent = layer._featureId || 'N/A';
}

function closeGeojsonModal() {
    const modal = document.getElementById('geojson-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentFeature = null;
}

// Manter compatibilidade com código antigo
function closeAttributeModal() {
    closeGeojsonModal();
}

async function saveAttributes() {
    if (!currentFeature) return;
    
    try {
        // Coletar dados do formulário
        const properties = {};
        const form = document.getElementById('gleba-attributes-form');
        const formData = new FormData(form);
        
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                properties[key] = value.trim();
            }
        }
        
        // Criar ou atualizar feature
        if (!currentFeature.feature) {
            currentFeature.feature = {
                type: 'Feature',
                properties: {},
                geometry: currentFeature.toGeoJSON().geometry
            };
        }
        
        currentFeature.feature.properties = properties;
        
        // Aplicar estilos se definidos
        applyFeatureStyles(currentFeature, properties);
        
        // Atualizar popup
        updateFeaturePopup(currentFeature);
        
        // Salvar no banco de dados
        await saveFeatureToDatabase(currentFeature);
        
        // Atualizar lista de camadas
        updateLayersList();
        
        closeAttributeModal();
        
        console.log('✅ Atributos salvos com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao salvar atributos:', error);
        alert('Erro ao salvar atributos');
    }
}

async function saveGeojsonAttributes() {
    if (!currentFeature) return;
    
    try {
    
    // Coletar dados do formulário geojson
    const properties = {};
    
    // Informações da Gleba
    const glebaNumero = document.getElementById('gleba-numero');
    const glebaNome = document.getElementById('gleba-nome');
    const glebaArea = document.getElementById('gleba-area');
    const glebaPerimetro = document.getElementById('gleba-perimetro');
    
    if (glebaNumero) properties.no_gleba = glebaNumero.value;
    if (glebaNome) properties.nome_gleba = glebaNome.value;
    if (glebaArea) properties.area = glebaArea.value;
    if (glebaPerimetro) properties.perimetro = glebaPerimetro.value;
    
    // Proprietário
    const proprietarioNome = document.getElementById('proprietario-nome');
    const proprietarioCpf = document.getElementById('proprietario-cpf');
    const proprietarioRg = document.getElementById('proprietario-rg');
    
    if (proprietarioNome) properties.proprietario = proprietarioNome.value;
    if (proprietarioCpf) properties.cpf = proprietarioCpf.value;
    if (proprietarioRg) properties.rg = proprietarioRg.value;
    
    // Endereço
    const enderecoRua = document.getElementById('endereco-rua');
    const enderecoBairro = document.getElementById('endereco-bairro');
    const enderecoQuadra = document.getElementById('endereco-quadra');
    const enderecoCep = document.getElementById('endereco-cep');
    const enderecoCidade = document.getElementById('endereco-cidade');
    const enderecoUf = document.getElementById('endereco-uf');
    
    if (enderecoRua) properties.rua = enderecoRua.value;
    if (enderecoBairro) properties.bairro = enderecoBairro.value;
    if (enderecoQuadra) properties.quadra = enderecoQuadra.value;
    if (enderecoCep) properties.cep = enderecoCep.value;
    if (enderecoCidade) properties.cidade = enderecoCidade.value;
    if (enderecoUf) properties.uf = enderecoUf.value;
    
    // Testadas
    const testadaFrente = document.getElementById('testada-frente');
    const testadaLd = document.getElementById('testada-ld');
    const testadaLe = document.getElementById('testada-le');
    const testadaF = document.getElementById('testada-f');
    
    if (testadaFrente) properties.testada_frente = testadaFrente.value;
    if (testadaLd) properties.testada_ld = testadaLd.value;
    if (testadaLe) properties.testada_le = testadaLe.value;
    if (testadaF) properties.testada_f = testadaF.value;
    
    // Imóvel
    const imovelMatricula = document.getElementById('imovel-matricula');
    const zoneamento = document.getElementById('zoneamento');
    const finalidade = document.getElementById('finalidade');
    const padraoConstrutivo = document.getElementById('padrao-construtivo');
    const situacaoFundiaria = document.getElementById('situacao-fundiaria');
    const ocupacaoAtual = document.getElementById('ocupacao-atual');
    const descricaoImovel = document.getElementById('descricao-imovel');
    
    if (imovelMatricula) properties.matricula = imovelMatricula.value;
    if (zoneamento) properties.zoneamento = zoneamento.value;
    if (finalidade) properties.finalidade = finalidade.value;
    if (padraoConstrutivo) properties.padrao_construtivo = padraoConstrutivo.value;
    if (situacaoFundiaria) properties.situacao_fundiaria = situacaoFundiaria.value;
    if (ocupacaoAtual) properties.ocupacao_atual = ocupacaoAtual.value;
    if (descricaoImovel) properties.descricao_imovel = descricaoImovel.value;
    
    // Aplicar propriedades à feature
    if (!currentFeature.feature) {
        currentFeature.feature = { type: 'Feature', properties: {}, geometry: null };
    }
    
    currentFeature.feature.properties = { ...currentFeature.feature.properties, ...properties };
    
    // Aplicar estilos se definidos
    applyFeatureStyles(currentFeature, properties);
    
    // Atualizar popup
    updateFeaturePopup(currentFeature);
    
    // Salvar no banco de dados
    await saveFeatureToDatabase(currentFeature);
    
    // Atualizar lista de camadas
    updateLayersList();
    
    closeGeojsonModal();
    
    console.log('✅ Dados da gleba salvos com sucesso!');
    
    } catch (error) {
        console.error('❌ Erro ao salvar dados da gleba:', error);
        alert('Erro ao salvar dados da gleba');
    }
}

function applyFeatureStyles(layer, properties) {
    const style = {};
    
    if (properties['stroke']) {
        style.color = properties['stroke'];
    }
    if (properties['stroke-width']) {
        style.weight = parseInt(properties['stroke-width']);
    }
    if (properties['stroke-opacity']) {
        style.opacity = parseFloat(properties['stroke-opacity']);
    }
    if (properties['fill']) {
        style.fillColor = properties['fill'];
    }
    if (properties['fill-opacity']) {
        style.fillOpacity = parseFloat(properties['fill-opacity']);
    }
    
    if (Object.keys(style).length > 0 && layer.setStyle) {
        layer.setStyle(style);
    }
}

function updateFeaturePopup(layer) {
    const properties = layer.feature ? layer.feature.properties || {} : {};
    
    let popupContent = '<div class="feature-popup">';
    
    // Título da gleba
    const nomeGleba = properties.nome_gleba || properties.no_gleba || 'Gleba';
    popupContent += `<h6><i class="fas fa-map-marked-alt"></i> ${nomeGleba}</h6>`;
    
    // Informações principais
    if (properties.no_gleba) {
        popupContent += `<p><strong>Nº:</strong> ${properties.no_gleba}</p>`;
    }
    
    if (properties.area) {
        popupContent += `<p><strong>Área:</strong> ${properties.area} m²</p>`;
    }
    
    if (properties.proprietario) {
        popupContent += `<p><strong>Proprietário:</strong> ${properties.proprietario}</p>`;
    }
    
    if (properties.classe_imovel) {
        popupContent += `<p><strong>Classe:</strong> ${properties.classe_imovel}</p>`;
    }
    
    if (properties.endereco || properties.rua) {
        const endereco = properties.rua || 'Endereço não informado';
        popupContent += `<p><strong>Endereço:</strong> ${endereco}</p>`;
    }
    
    // Se não há informações principais, mostrar mensagem
    if (!properties.nome_gleba && !properties.no_gleba && !properties.proprietario) {
        popupContent += '<p style="color: #666; font-style: italic;">Clique para adicionar informações</p>';
    }
    
    popupContent += '<div class="popup-actions" style="margin-top: 10px; text-align: center;">';
    popupContent += `<button onclick="editFeature('${layer._featureId}')" style="
        background: #2e60ff; 
        color: white; 
        border: none; 
        padding: 6px 12px; 
        border-radius: 4px; 
        font-size: 12px; 
        cursor: pointer;
        transition: background 0.2s;
    " onmouseover="this.style.background='#1e40af'" onmouseout="this.style.background='#2e60ff'">
        <i class="fas fa-edit"></i> Editar Gleba
    </button>`;
    popupContent += '</div>';
    popupContent += '</div>';
    
    layer.bindPopup(popupContent);
}

function editFeature(featureId) {
    // Encontrar feature pelo ID
    drawnItems.eachLayer(function(layer) {
        if (layer._featureId === featureId) {
            currentFeature = layer;
            openAttributeModal(layer);
        }
    });
}

function deleteCurrentFeature() {
    if (currentFeature && confirm('Tem certeza que deseja deletar esta feature?')) {
        // Remover do banco de dados
        deleteFeatureFromDatabase(currentFeature);
        
        // Remover do mapa
        drawnItems.removeLayer(currentFeature);
        
        // Atualizar lista de camadas
        updateLayersList();
        
        closeAttributeModal();
        alert('Feature deletada com sucesso!');
    }
}

function updateFeatureInfo(layer) {
    // Atualizar informações da feature após edição
    if (layer.feature) {
        layer.feature.geometry = layer.toGeoJSON().geometry;
        updateFeaturePopup(layer);
        saveFeatureToDatabase(layer);
    }
}

// Funções de integração com banco de dados
async function saveFeatureToDatabase(layer) {
    try {
        // Gerar ID único se não existir
        if (!layer._featureId) {
            layer._featureId = 'feature_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        const featureData = {
            id: layer._featureId,
            type: 'Feature',
            geometry: layer.toGeoJSON().geometry,
            properties: layer.feature ? layer.feature.properties : {}
        };
        
        console.log('Salvando feature no banco:', featureData);
        
        const response = await fetch('/api/features', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify(featureData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao salvar feature');
        }
        
        const result = await response.json();
        console.log('✅ Feature salva no banco de dados:', result);
        
        // Atualizar ID se foi gerado pelo servidor
        if (result.id && result.id !== layer._featureId) {
            layer._featureId = result.id;
        }
        
    } catch (error) {
        console.error('❌ Erro salvando feature:', error);
        // Não mostrar alert para não interromper fluxo
        console.log('Feature será mantida apenas na memória');
    }
}

async function deleteFeatureFromDatabase(layer) {
    try {
        if (!layer._featureId) return;
        
        const response = await fetch(`/api/features/${layer._featureId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erro ao deletar feature');
        }
        
        console.log('Feature deletada do banco de dados');
        
    } catch (error) {
        console.error('Erro deletando feature:', error);
        alert('Erro ao deletar feature do banco de dados');
    }
}

// Funções de exportação
function exportAllFeatures() {
    const features = [];
    
    drawnItems.eachLayer(function(layer) {
        const feature = {
            type: 'Feature',
            geometry: layer.toGeoJSON().geometry,
            properties: layer.feature ? layer.feature.properties : {}
        };
        features.push(feature);
    });
    
    const featureCollection = {
        type: 'FeatureCollection',
        features: features
    };
    
    return featureCollection;
}

function downloadGeoJSON() {
    const geojson = exportAllFeatures();
    const dataStr = JSON.stringify(geojson, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = 'features_' + new Date().toISOString().split('T')[0] + '.geojson';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Carregar features existentes do banco de dados
async function loadExistingFeatures() {
    try {
        console.log('🔄 Carregando features existentes do banco...');
        
        // Aguardar autenticação antes de carregar features
        let retries = 0;
        let authResponse;
        
        while (retries < 5) {
            try {
                authResponse = await fetch('/api/auth/check', {
                    method: 'GET',
                    credentials: 'same-origin'
                });
                
                if (authResponse.ok) {
                    const authData = await authResponse.json();
                    if (authData.authenticated) {
                        console.log('✅ Usuário autenticado, carregando features...');
                        break;
                    }
                }
            } catch (authError) {
                console.log(`⚠️ Tentativa ${retries + 1} de verificação de auth falhou:`, authError);
            }
            
            retries++;
            await new Promise(resolve => setTimeout(resolve, 1000)); // Aguardar 1s entre tentativas
        }
        
        if (retries >= 5) {
            console.log('❌ Falha na autenticação após 5 tentativas, pulando carregamento');
            return;
        }
        
        const response = await fetch('/api/features', {
            method: 'GET',
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.log('⚠️ Usuário não autenticado, pulando carregamento');
                return;
            }
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📊 Dados recebidos do banco:', data);
        console.log('📊 Status da resposta:', data.status, 'Total:', data.total);
        
        if (data.features && data.features.length > 0) {
            console.log(`📥 Carregando ${data.features.length} features do banco`);
            
            // Verificar se drawnItems existe
            if (!drawnItems) {
                console.error('❌ drawnItems não definido!');
                return;
            }
            
            // Limpar features existentes primeiro
            console.log('🧹 Limpando features existentes...');
            drawnItems.clearLayers();
            
            let successCount = 0;
            let errorCount = 0;
            
            for (const featureData of data.features) {
                try {
                    console.log(`🔄 Carregando feature ${featureData.id}:`, featureData);
                    await loadFeatureToMap(featureData);
                    successCount++;
                } catch (loadError) {
                    console.error(`❌ Erro carregando feature ${featureData.id}:`, loadError);
                    errorCount++;
                }
            }
            
            console.log(`✅ Carregamento concluído: ${successCount} sucessos, ${errorCount} erros`);
            
            // Atualizar lista de camadas após carregar todas
            if (typeof updateLayersList === 'function') {
                updateLayersList();
            } else {
                console.warn('⚠️ updateLayersList não é uma função');
            }
            
            // Verificar quantas features foram realmente adicionadas
            const layerCount = drawnItems.getLayers().length;
            console.log(`📊 Total de layers no mapa: ${layerCount}`);
            
            console.log('✅ Features carregadas com sucesso do banco');
        } else {
            console.log('ℹ️ Nenhuma feature encontrada no banco - data.features:', data.features);
        }
        
    } catch (error) {
        console.error('❌ Erro carregando features do banco:', error);
    }
}

async function loadFeatureToMap(featureData) {
    try {
        // Criar layer baseado na geometria
        let layer;
        const geometry = featureData.geometry;
        
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
            case 'Circle':
                // Para círculos, usar L.circle se as propriedades estiverem disponíveis
                if (featureData.properties && featureData.properties.radius) {
                    layer = L.circle([geometry.coordinates[1], geometry.coordinates[0]], {
                        radius: featureData.properties.radius
                    });
                } else {
                    layer = L.marker([geometry.coordinates[1], geometry.coordinates[0]]);
                }
                break;
            default:
                console.warn('Tipo de geometria não suportado:', geometry.type);
                return;
        }
        
        // Configurar feature
        layer._featureId = featureData.id;
        layer.feature = {
            type: 'Feature',
            geometry: geometry,
            properties: featureData.properties || {}
        };
        
        // Aplicar estilos se definidos
        if (featureData.properties) {
            applyFeatureStyles(layer, featureData.properties);
        }
        
        // Adicionar ao grupo de features
        drawnItems.addLayer(layer);
        
        // Configurar evento de clique
        layer.on('click', function() {
            currentFeature = layer;
            openAttributeModal(layer);
        });
        
        // Atualizar popup
        updateFeaturePopup(layer);
        
    } catch (error) {
        console.error('Erro carregando feature individual:', error);
    }
}

// ===== GERENCIAMENTO DE CAMADAS =====
function updateLayersList() {
    const layerControls = document.getElementById('layer-controls');
    if (!layerControls) return;
    
    layerControls.innerHTML = '';
    
    const layers = [];
    drawnItems.eachLayer(function(layer) {
        if (layer.feature && layer.feature.properties) {
            const props = layer.feature.properties;
            const layerInfo = {
                id: layer._featureId,
                name: props.nome_gleba || props.no_gleba || 'Gleba sem nome',
                type: layer.feature.geometry.type,
                layer: layer
            };
            layers.push(layerInfo);
        }
    });
    
    if (layers.length === 0) {
        layerControls.innerHTML = '<p style="color: rgba(255,255,255,0.6); text-align: center; padding: 20px;">Nenhuma camada criada</p>';
        return;
    }
    
    layers.forEach(layerInfo => {
        const layerElement = createLayerElement(layerInfo);
        layerControls.appendChild(layerElement);
    });
}

function createLayerElement(layerInfo) {
    const layerDiv = document.createElement('div');
    layerDiv.className = 'layer-item';
    
    // Verificar se a camada está visível
    const isVisible = layerInfo.layer._isVisible !== false; // por padrão é true
    const checkedAttribute = isVisible ? 'checked' : '';
    
    layerDiv.innerHTML = `
        <div class="layer-header">
            <div class="layer-info">
                <div class="layer-icon">
                    <i class="fas ${getLayerIcon(layerInfo.type)}"></i>
                </div>
                <div class="layer-details">
                    <h5 class="layer-name">${layerInfo.name}</h5>
                    <span class="layer-type">${getLayerTypeLabel(layerInfo.type)}</span>
                </div>
            </div>
            <div class="layer-actions">
                <label class="layer-toggle">
                    <input type="checkbox" ${checkedAttribute} onchange="toggleLayer('${layerInfo.id}')">
                    <span class="toggle-slider"></span>
                </label>
                <button class="layer-zoom-btn" onclick="zoomToLayer('${layerInfo.id}')" title="Zoom para camada">
                    <i class="fas fa-search-plus"></i>
                </button>
                <button class="layer-edit-btn" onclick="editLayerFeature('${layerInfo.id}')" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        </div>
    `;
    return layerDiv;
}

function getLayerIcon(geometryType) {
    switch(geometryType) {
        case 'Point': return 'fa-map-pin';
        case 'LineString': return 'fa-route';
        case 'Polygon': return 'fa-draw-polygon';
        case 'Circle': return 'fa-circle';
        default: return 'fa-map-marked-alt';
    }
}

function getLayerTypeLabel(geometryType) {
    switch(geometryType) {
        case 'Point': return 'Ponto';
        case 'LineString': return 'Linha';
        case 'Polygon': return 'Polígono';
        case 'Circle': return 'Círculo';
        default: return 'Feature';
    }
}

function toggleLayer(layerId) {
    drawnItems.eachLayer(function(layer) {
        if (layer._featureId === layerId) {
            if (window.map.hasLayer(layer)) {
                // Remover apenas do mapa, mas manter no drawnItems
                window.map.removeLayer(layer);
                layer._isVisible = false;
                console.log('Layer ocultada:', layerId);
            } else {
                // Adicionar de volta ao mapa
                window.map.addLayer(layer);
                layer._isVisible = true;
                console.log('Layer exibida:', layerId);
            }
        }
    });
    
    // Atualizar a lista de camadas para refletir o estado atual
    setTimeout(() => {
        updateLayersList();
    }, 100);
}

function zoomToLayer(layerId) {
    drawnItems.eachLayer(function(layer) {
        if (layer._featureId === layerId) {
            if (layer.getBounds) {
                // Fazer zoom mais próximo com padding menor e zoom mínimo mais alto
                const bounds = layer.getBounds();
                window.map.fitBounds(bounds, {
                    padding: [10, 10], // Padding menor para zoom mais próximo
                    maxZoom: 18 // Zoom mínimo mais alto
                });
            } else if (layer.getLatLng) {
                // Para pontos, usar zoom ainda mais próximo
                window.map.setView(layer.getLatLng(), 19);
            }
        }
    });
}

function editLayerFeature(layerId) {
    drawnItems.eachLayer(function(layer) {
        if (layer._featureId === layerId) {
            currentFeature = layer;
            openAttributeModal(layer);
        }
    });
}

// ===== FUNÇÃO PARA LIMPAR FEATURES ANTIGAS =====
async function clearAllFeatures() {
    if (!confirm('Tem certeza que deseja remover TODAS as features do banco de dados? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/features/clear-all', {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            // Limpar do mapa também
            drawnItems.clearLayers();
            updateLayersList();
            alert('Todas as features foram removidas com sucesso!');
        } else {
            throw new Error('Erro ao limpar features');
        }
    } catch (error) {
        console.error('Erro limpando features:', error);
        alert('Erro ao limpar features do banco de dados');
    }
}

// Função para limpar apenas do mapa (emergência)
function clearMapOnly() {
    if (confirm('Limpar apenas as features visíveis no mapa? (Não afeta o banco de dados)')) {
        drawnItems.clearLayers();
        updateLayersList();
        console.log('Features removidas apenas do mapa');
    }
}

// ===== LABELS DE ÁREA E PERÍMETRO =====
let geometryLabels = new L.LayerGroup();

function addGeometryLabel(layer) {
    const geom = layer.toGeoJSON();
    
    if (geom.geometry.type === 'Polygon') {
        try {
            // Calcular centroide do polígono
            const bounds = layer.getBounds();
            const center = bounds.getCenter();
            
            // Calcular área e perímetro
            let area = 0;
            let perimeter = 0;
            
            if (typeof L.GeometryUtil !== 'undefined' && L.GeometryUtil.geodesicArea) {
                try {
                    area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
                } catch (e) {
                    // Cálculo alternativo
                    const coords = layer.getLatLngs()[0];
                    for (let i = 0; i < coords.length; i++) {
                        const j = (i + 1) % coords.length;
                        area += coords[i].lat * coords[j].lng;
                        area -= coords[j].lat * coords[i].lng;
                    }
                    area = Math.abs(area) / 2 * 111319.5 * 111319.5;
                }
            } else {
                // Cálculo alternativo
                const coords = layer.getLatLngs()[0];
                for (let i = 0; i < coords.length; i++) {
                    const j = (i + 1) % coords.length;
                    area += coords[i].lat * coords[j].lng;
                    area -= coords[j].lat * coords[i].lng;
                }
                area = Math.abs(area) / 2 * 111319.5 * 111319.5;
            }
            
            // Calcular perímetro
            const coords = layer.getLatLngs()[0];
            for (let i = 0; i < coords.length; i++) {
                const nextIndex = (i + 1) % coords.length;
                perimeter += coords[i].distanceTo(coords[nextIndex]);
            }
            
            // Criar label com área e perímetro
            const labelText = `Área: ${area.toFixed(0)} m²\nPerímetro: ${perimeter.toFixed(0)} m`;
            
            const label = L.marker(center, {
                icon: L.divIcon({
                    className: 'geometry-label',
                    html: `<div class="label-content">${labelText.replace('\n', '<br>')}</div>`,
                    iconSize: [120, 40],
                    iconAnchor: [60, 20]
                })
            });
            
            // Associar label ao layer
            label._parentLayer = layer;
            layer._geometryLabel = label;
            
            // Adicionar ao grupo de labels
            geometryLabels.addLayer(label);
            
        } catch (error) {
            console.warn('Erro criando label de geometria:', error);
        }
    }
}

function removeGeometryLabel(layer) {
    if (layer._geometryLabel) {
        geometryLabels.removeLayer(layer._geometryLabel);
        layer._geometryLabel = null;
    }
}

function updateGeometryLabel(layer) {
    removeGeometryLabel(layer);
    addGeometryLabel(layer);
}

// Adicionar grupo de labels ao mapa quando disponível
function initializeGeometryLabels() {
    if (window.map && !window.map.hasLayer(geometryLabels)) {
        window.map.addLayer(geometryLabels);
        console.log('✅ Labels de geometria inicializados');
    }
}

// Expor funções globalmente para uso em outros scripts
window.GeoJsonTools = {
    exportAllFeatures,
    downloadGeoJSON,
    editFeature,
    saveFeatureToDatabase,
    deleteFeatureFromDatabase,
    loadExistingFeatures,
    updateLayersList,
    clearAllFeatures,
    clearMapOnly,
    addGeometryLabel,
    removeGeometryLabel,
    updateGeometryLabel
};