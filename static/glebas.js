// WEBAG Professional - Sistema de Glebas
// Integração das ferramentas de desenho vetorial com backend

// Variáveis globais para desenho
let map = null;
let drawnItems = null;
let drawControl = null;
let isEditingGleba = false;
let currentGleba = null;

// Configuração de estilos para glebas
const glebaStyle = {
    color: '#2e60ff',
    weight: 3,
    opacity: 0.8,
    fillColor: '#2e60ff',
    fillOpacity: 0.2
};

// Inicializar sistema de glebas
function initGlebasSystem() {
    console.log('Iniciando sistema de glebas...');
    
    // Verificar se o mapa está disponível
    if (!window.map) {
        console.error('Mapa não encontrado!');
        return;
    }
    
    map = window.map;
    
    // Criar grupo para glebas desenhadas
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    
    // Configurar controles de desenho
    drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            polyline: false,
            circle: false,
            rectangle: false,
            marker: false,
            circlemarker: false,
            polygon: {
                allowIntersection: false,
                showArea: true,
                drawError: {
                    color: '#e1e100',
                    message: '<strong>Erro:</strong> Polígono não pode se intersectar!'
                },
                shapeOptions: glebaStyle
            }
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    
    map.addControl(drawControl);
    
    // Event listeners para desenho
    setupDrawEventListeners();
    
    // Carregar glebas existentes
    loadExistingGlebas();
    
    console.log('✅ Sistema de glebas inicializado');
}

// Configurar event listeners para desenho
function setupDrawEventListeners() {
    // Quando um polígono é criado
    map.on(L.Draw.Event.CREATED, function(e) {
        const layer = e.layer;
        
        // Adicionar ao grupo de glebas
        drawnItems.addLayer(layer);
        
        // Calcular área e perímetro
        const area = calculatePolygonArea(layer);
        const perimeter = calculatePolygonPerimeter(layer);
        
        // Abrir painel de edição com dados calculados
        openGlebaEditPanel({
            geometry: layer.toGeoJSON().geometry,
            area: area,
            perimetro: perimeter,
            isNew: true,
            layer: layer
        });
    });
    
    // Quando um polígono é editado
    map.on(L.Draw.Event.EDITED, function(e) {
        const layers = e.layers;
        layers.eachLayer(function(layer) {
            // Recalcular área e perímetro
            const area = calculatePolygonArea(layer);
            const perimeter = calculatePolygonPerimeter(layer);
            
            // Atualizar dados da gleba
            if (layer.glebaData) {
                layer.glebaData.area = area;
                layer.glebaData.perimetro = perimeter;
                layer.glebaData.geometry = layer.toGeoJSON().geometry;
                
                // Auto-salvar se já existir no banco
                if (layer.glebaData.id) {
                    updateGleba(layer.glebaData.id, layer.glebaData);
                }
            }
        });
    });
    
    // Quando um polígono é deletado
    map.on(L.Draw.Event.DELETED, function(e) {
        const layers = e.layers;
        layers.eachLayer(function(layer) {
            if (layer.glebaData && layer.glebaData.id) {
                if (confirm(`Deseja realmente deletar a gleba ${layer.glebaData.no_gleba}?`)) {
                    deleteGleba(layer.glebaData.id);
                }
            }
        });
    });
}

// Calcular área do polígono em m²
function calculatePolygonArea(layer) {
    if (!layer.getLatLngs) return 0;
    
    const latlngs = layer.getLatLngs()[0]; // Pegar primeiro anel
    let area = 0;
    
    // Usar fórmula de Shoelace para cálculo aproximado
    for (let i = 0; i < latlngs.length; i++) {
        const j = (i + 1) % latlngs.length;
        const lat1 = latlngs[i].lat * Math.PI / 180;
        const lat2 = latlngs[j].lat * Math.PI / 180;
        const lng1 = latlngs[i].lng * Math.PI / 180;
        const lng2 = latlngs[j].lng * Math.PI / 180;
        
        area += (lng2 - lng1) * Math.sin((lat1 + lat2) / 2);
    }
    
    // Converter para m² (aproximação usando raio da Terra)
    const earthRadius = 6371000; // metros
    area = Math.abs(area * earthRadius * earthRadius / 2);
    
    return Math.round(area * 100) / 100; // Arredondar para 2 casas decimais
}

// Calcular perímetro do polígono em metros
function calculatePolygonPerimeter(layer) {
    if (!layer.getLatLngs) return 0;
    
    const latlngs = layer.getLatLngs()[0];
    let perimeter = 0;
    
    for (let i = 0; i < latlngs.length; i++) {
        const j = (i + 1) % latlngs.length;
        const distance = map.distance(latlngs[i], latlngs[j]);
        perimeter += distance;
    }
    
    return Math.round(perimeter * 100) / 100;
}

// Abrir painel de edição de gleba
function openGlebaEditPanel(glebaData) {
    currentGleba = glebaData;
    isEditingGleba = true;
    
    // Mostrar painel
    const editPanel = document.getElementById('edit-panel');
    if (editPanel) {
        editPanel.style.display = 'block';
        
        // Preencher formulário
        fillGlebaForm(glebaData);
        
        // Focar no primeiro campo
        const firstInput = editPanel.querySelector('input[type="text"]');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

// Preencher formulário com dados da gleba
function fillGlebaForm(glebaData) {
    // Limpar formulário primeiro
    const form = document.getElementById('gleba-form');
    if (form) {
        form.reset();
    }
    
    // Preencher campos básicos
    setFieldValue('area', formatArea(glebaData.area));
    setFieldValue('perimetro', formatDistance(glebaData.perimetro));
    
    // Se não for nova, preencher outros dados
    if (!glebaData.isNew && glebaData.id) {
        setFieldValue('no_gleba', glebaData.no_gleba);
        setFieldValue('nome_gleba', glebaData.nome_gleba);
        setFieldValue('proprietario', glebaData.proprietario);
        setFieldValue('cpf', glebaData.cpf);
        setFieldValue('rg', glebaData.rg);
        setFieldValue('rua', glebaData.rua);
        setFieldValue('bairro', glebaData.bairro);
        setFieldValue('quadra', glebaData.quadra);
        setFieldValue('cep', glebaData.cep);
        setFieldValue('cidade', glebaData.cidade);
        setFieldValue('uf', glebaData.uf);
    } else {
        // Para nova gleba, gerar número automático
        generateGlebaNumber();
    }
}

// Definir valor em campo do formulário
function setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && value !== null && value !== undefined) {
        field.value = value;
    }
}

// Gerar número automático para gleba
function generateGlebaNumber() {
    const timestamp = new Date().getTime();
    const glebaNumber = `GL-${timestamp.toString().slice(-6)}`;
    setFieldValue('no_gleba', glebaNumber);
}

// Salvar gleba
async function saveCurrentGleba() {
    if (!currentGleba) {
        alert('Nenhuma gleba selecionada para salvar');
        return;
    }
    
    try {
        // Coletar dados do formulário
        const formData = collectFormData();
        
        // Validar dados obrigatórios
        if (!formData.no_gleba) {
            alert('Número da gleba é obrigatório');
            document.getElementById('no_gleba').focus();
            return;
        }
        
        // Adicionar geometria e cálculos
        formData.geometry = currentGleba.geometry;
        formData.area = currentGleba.area;
        formData.perimetro = currentGleba.perimetro;
        
        let response;
        if (currentGleba.isNew) {
            // Criar nova gleba
            response = await fetch('/api/glebas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
        } else {
            // Atualizar gleba existente
            response = await fetch(`/api/glebas/${currentGleba.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
        }
        
        const result = await response.json();
        
        if (response.ok) {
            // Sucesso
            alert(`Gleba ${formData.no_gleba} salva com sucesso!`);
            
            // Atualizar dados da camada
            if (currentGleba.layer) {
                currentGleba.layer.glebaData = {
                    ...formData,
                    id: result.id || currentGleba.id
                };
                
                // Atualizar popup da camada
                updateLayerPopup(currentGleba.layer);
            }
            
            // Fechar painel
            closeGlebaEditPanel();
            
            // Recarregar lista de glebas
            loadExistingGlebas();
            
        } else {
            throw new Error(result.error || 'Erro ao salvar gleba');
        }
        
    } catch (error) {
        console.error('Erro salvando gleba:', error);
        alert(`Erro ao salvar gleba: ${error.message}`);
    }
}

// Coletar dados do formulário
function collectFormData() {
    const formFields = [
        'no_gleba', 'nome_gleba', 'proprietario', 'cpf', 'rg',
        'rua', 'bairro', 'quadra', 'cep', 'cidade', 'uf',
        'testada_frente', 'testada_fundo', 'testada_esquerda', 'testada_direita',
        'confrontacao_frente', 'confrontacao_fundo', 'confrontacao_esquerda', 'confrontacao_direita',
        'valor_imovel', 'matricula', 'inscricao_municipal', 'observacoes'
    ];
    
    const data = {};
    
    formFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            let value = field.value.trim();
            
            // Converter campos numéricos
            if (['testada_frente', 'testada_fundo', 'testada_esquerda', 'testada_direita', 'valor_imovel'].includes(fieldId)) {
                value = value ? parseFloat(value) : null;
            }
            
            data[fieldId] = value || null;
        }
    });
    
    return data;
}

// Fechar painel de edição
function closeGlebaEditPanel() {
    const editPanel = document.getElementById('edit-panel');
    if (editPanel) {
        editPanel.style.display = 'none';
    }
    
    currentGleba = null;
    isEditingGleba = false;
}

// Carregar glebas existentes do servidor
async function loadExistingGlebas() {
    try {
        const response = await fetch('/api/glebas');
        const data = await response.json();
        
        if (response.ok && data.glebas) {
            // Limpar glebas existentes
            drawnItems.clearLayers();
            
            // Adicionar cada gleba ao mapa
            data.glebas.forEach(gleba => {
                if (gleba.geometry) {
                    addGlebaToMap(gleba);
                }
            });
            
            console.log(`✅ ${data.glebas.length} glebas carregadas`);
        }
        
    } catch (error) {
        console.error('Erro carregando glebas:', error);
    }
}

// Adicionar gleba ao mapa
function addGlebaToMap(gleba) {
    try {
        // Criar layer do Leaflet a partir da geometria GeoJSON
        const layer = L.geoJSON(gleba.geometry, {
            style: glebaStyle
        }).getLayers()[0];
        
        // Adicionar dados da gleba ao layer
        layer.glebaData = gleba;
        
        // Adicionar popup com informações
        updateLayerPopup(layer);
        
        // Adicionar ao grupo de glebas
        drawnItems.addLayer(layer);
        
        // Adicionar event listener para edição
        layer.on('click', function() {
            openGlebaEditPanel({
                ...gleba,
                isNew: false,
                layer: layer
            });
        });
        
    } catch (error) {
        console.error('Erro adicionando gleba ao mapa:', error);
    }
}

// Atualizar popup da camada
function updateLayerPopup(layer) {
    if (!layer.glebaData) return;
    
    const gleba = layer.glebaData;
    const popupContent = `
        <div class="gleba-popup">
            <h6><i class="fas fa-map-marked-alt"></i> ${gleba.no_gleba}</h6>
            ${gleba.nome_gleba ? `<p><strong>Nome:</strong> ${gleba.nome_gleba}</p>` : ''}
            <p><strong>Área:</strong> ${formatArea(gleba.area)}</p>
            <p><strong>Perímetro:</strong> ${formatDistance(gleba.perimetro)}</p>
            ${gleba.proprietario ? `<p><strong>Proprietário:</strong> ${gleba.proprietario}</p>` : ''}
            <div class="popup-actions">
                <button class="btn btn-sm btn-primary" onclick="editGleba(${gleba.id})">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="btn btn-sm btn-success" onclick="exportGleba(${gleba.id})">
                    <i class="fas fa-download"></i> Exportar
                </button>
            </div>
        </div>
    `;
    
    layer.bindPopup(popupContent);
}

// Formatar área para exibição
function formatArea(area) {
    if (!area) return '0 m²';
    
    if (area < 10000) {
        return `${area.toLocaleString()} m²`;
    } else {
        const hectares = area / 10000;
        return `${hectares.toFixed(2)} ha (${area.toLocaleString()} m²)`;
    }
}

// Formatar distância para exibição
function formatDistance(distance) {
    if (!distance) return '0 m';
    
    if (distance < 1000) {
        return `${distance.toFixed(2)} m`;
    } else {
        const km = distance / 1000;
        return `${km.toFixed(3)} km`;
    }
}

// Editar gleba existente
async function editGleba(glebaId) {
    try {
        const response = await fetch(`/api/glebas/${glebaId}`);
        const gleba = await response.json();
        
        if (response.ok) {
            // Encontrar layer correspondente
            let targetLayer = null;
            drawnItems.eachLayer(function(layer) {
                if (layer.glebaData && layer.glebaData.id === glebaId) {
                    targetLayer = layer;
                }
            });
            
            openGlebaEditPanel({
                ...gleba,
                isNew: false,
                layer: targetLayer
            });
        }
        
    } catch (error) {
        console.error('Erro carregando gleba para edição:', error);
        alert('Erro carregando dados da gleba');
    }
}

// Exportar gleba
async function exportGleba(glebaId) {
    try {
        const response = await fetch(`/api/glebas/${glebaId}`);
        const gleba = await response.json();
        
        if (response.ok) {
            // Criar GeoJSON da gleba
            const geojson = {
                type: 'Feature',
                properties: {
                    no_gleba: gleba.no_gleba,
                    nome_gleba: gleba.nome_gleba,
                    area: gleba.area,
                    perimetro: gleba.perimetro,
                    proprietario: gleba.proprietario,
                    cpf: gleba.cpf,
                    created_at: gleba.created_at
                },
                geometry: gleba.geometry
            };
            
            // Download do arquivo
            const blob = new Blob([JSON.stringify(geojson, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `gleba_${gleba.no_gleba}.geojson`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            alert(`Gleba ${gleba.no_gleba} exportada com sucesso!`);
        }
        
    } catch (error) {
        console.error('Erro exportando gleba:', error);
        alert('Erro ao exportar gleba');
    }
}

// Máscaras para campos de entrada
function setupInputMasks() {
    // Máscara para CPF
    const cpfField = document.getElementById('cpf');
    if (cpfField) {
        cpfField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            e.target.value = value;
        });
    }
    
    // Máscara para CEP
    const cepField = document.getElementById('cep');
    if (cepField) {
        cepField.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{5})(\d)/, '$1-$2');
            e.target.value = value;
        });
    }
}

// Event listeners para botões
function setupGlebaEventListeners() {
    // Botão de salvar gleba
    const saveBtn = document.getElementById('save-gleba-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveCurrentGleba);
    }
    
    // Botão de fechar painel
    const closeBtn = document.getElementById('close-edit-panel');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeGlebaEditPanel);
    }
    
    // Configurar máscaras de input
    setupInputMasks();
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar inicialização do mapa
    setTimeout(() => {
        initGlebasSystem();
        setupGlebaEventListeners();
    }, 1000);
});

// Exportar funções para uso global
window.saveCurrentGleba = saveCurrentGleba;
window.closeGlebaEditPanel = closeGlebaEditPanel;
window.editGleba = editGleba;
window.exportGleba = exportGleba;