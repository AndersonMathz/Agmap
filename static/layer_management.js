/**
 * WEBAG Professional - Layer Management JavaScript
 * Sistema robusto de gerenciamento de camadas
 */

// ================================================
// GLOBAL VARIABLES
// ================================================

let currentProject = null;
let currentLayer = null;
let layerTree = null;
let layerGroups = [];
let layers = [];

// ================================================
// INITIALIZATION
// ================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando Layer Management System...');
    
    // Inicializar componentes
    initializeLayerTree();
    loadProjectInfo();
    loadLayerData();
    setupEventListeners();
    
    console.log('✅ Layer Management System carregado!');
});

function initializeLayerTree() {
    /**Inicializar árvore de camadas com JSTree*/
    $('#layer-tree').jstree({
        'core': {
            'themes': {
                'name': 'default-dark',
                'dots': true,
                'icons': true
            },
            'check_callback': true,
            'data': []
        },
        'contextmenu': {
            'items': function(node) {
                return getContextMenuItems(node);
            }
        },
        'dnd': {
            'is_draggable': function(node) {
                return node.length === 1 && node[0].type !== 'root';
            }
        },
        'types': {
            'root': {
                'icon': 'fas fa-folder-open',
                'valid_children': ['group', 'layer']
            },
            'group': {
                'icon': 'fas fa-folder',
                'valid_children': ['group', 'layer']
            },
            'layer': {
                'icon': 'fas fa-layer-group',
                'valid_children': []
            }
        },
        'plugins': ['contextmenu', 'dnd', 'types', 'wholerow']
    });
    
    // Event listeners da árvore
    $('#layer-tree').on('select_node.jstree', function(e, data) {
        onNodeSelect(data.node);
    });
    
    $('#layer-tree').on('move_node.jstree', function(e, data) {
        onNodeMove(data);
    });
}

function setupEventListeners() {
    /**Configurar event listeners*/
    
    // Layer opacity slider
    document.getElementById('layer-opacity').addEventListener('input', function(e) {
        const value = Math.round(e.target.value * 100);
        document.getElementById('opacity-value').textContent = value + '%';
    });
    
    // Context menu
    document.addEventListener('click', function(e) {
        hideContextMenu();
    });
    
    // Form auto-save
    const autoSaveFields = [
        'layer-display-name', 'layer-description', 'layer-group',
        'layer-status', 'layer-display-order', 'layer-visible',
        'layer-selectable', 'layer-editable'
    ];
    
    autoSaveFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', debounce(autoSaveLayer, 1000));
        }
    });
}

// ================================================
// DATA LOADING
// ================================================

async function loadProjectInfo() {
    /**Carregar informações do projeto*/
    try {
        // Por enquanto, usar dados mock
        currentProject = {
            id: 'proj_default',
            name: 'Projeto Principal',
            organization: 'WEBAG Professional'
        };
        
        document.getElementById('project-info').textContent = 
            `Projeto: ${currentProject.name}`;
        
    } catch (error) {
        console.error('Erro carregando projeto:', error);
        showToast('Erro ao carregar informações do projeto', 'error');
    }
}

async function loadLayerData() {
    /**Carregar dados das camadas e grupos*/
    try {
        showLoading(true);
        
        // Carregar grupos de camadas
        await loadLayerGroups();
        
        // Carregar camadas
        await loadLayers();
        
        // Atualizar árvore
        updateLayerTree();
        
        // Atualizar estatísticas
        updateStatistics();
        
    } catch (error) {
        console.error('Erro carregando dados:', error);
        showToast('Erro ao carregar dados das camadas', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadLayerGroups() {
    /**Carregar grupos de camadas*/
    try {
        const response = await fetch(`/api/v2/projects/${currentProject.id}/layer-groups`);
        
        if (response.ok) {
            const data = await response.json();
            layerGroups = data.layer_groups || [];
        } else {
            // Fallback para dados mock
            layerGroups = getMockLayerGroups();
        }
        
        // Atualizar dropdowns
        updateGroupDropdowns();
        
    } catch (error) {
        console.log('API não disponível, usando dados mock');
        layerGroups = getMockLayerGroups();
        updateGroupDropdowns();
    }
}

async function loadLayers() {
    /**Carregar camadas*/
    try {
        const response = await fetch(`/api/v2/projects/${currentProject.id}/layers`);
        
        if (response.ok) {
            const data = await response.json();
            layers = data.layers || [];
        } else {
            // Fallback para dados mock
            layers = getMockLayers();
        }
        
    } catch (error) {
        console.log('API não disponível, usando dados mock');
        layers = getMockLayers();
    }
}

function getMockLayerGroups() {
    /**Dados mock para grupos*/
    return [
        {
            id: 'group_base',
            name: 'Camadas Base',
            description: 'Camadas base do sistema',
            display_order: 0,
            is_expanded: true,
            is_visible: true,
            children: [],
            layers: []
        },
        {
            id: 'group_osm',
            name: 'OpenStreetMap',
            description: 'Dados do OpenStreetMap',
            display_order: 1,
            is_expanded: true,
            is_visible: true,
            children: [],
            layers: []
        },
        {
            id: 'group_glebas',
            name: 'Glebas',
            description: 'Glebas cadastradas',
            display_order: 2,
            is_expanded: true,
            is_visible: true,
            children: [],
            layers: []
        },
        {
            id: 'group_analysis',
            name: 'Análises',
            description: 'Camadas de análise',
            display_order: 3,
            is_expanded: false,
            is_visible: true,
            children: [],
            layers: []
        }
    ];
}

function getMockLayers() {
    /**Dados mock para camadas*/
    return [
        {
            id: 'layer_001',
            name: 'edificios',
            display_name: 'Edifícios',
            description: 'Edificações urbanas do OpenStreetMap',
            layer_type: 'vector',
            geometry_type: 'Polygon',
            layer_group_id: 'group_osm',
            status: 'active',
            feature_count: 23193,
            is_visible: true,
            is_selectable: true,
            is_editable: true,
            opacity: 0.8,
            display_order: 0,
            created_by: 'admin_super',
            created_at: '2024-07-12T10:00:00Z'
        },
        {
            id: 'layer_002',
            name: 'estradas',
            display_name: 'Estradas',
            description: 'Malha viária completa',
            layer_type: 'vector',
            geometry_type: 'LineString',
            layer_group_id: 'group_osm',
            status: 'active',
            feature_count: 35158,
            is_visible: true,
            is_selectable: true,
            is_editable: false,
            opacity: 1.0,
            display_order: 1,
            created_by: 'admin_super',
            created_at: '2024-07-12T10:00:00Z'
        },
        {
            id: 'layer_003',
            name: 'glebas_urbanas',
            display_name: 'Glebas Urbanas',
            description: 'Glebas urbanas cadastradas',
            layer_type: 'vector',
            geometry_type: 'Polygon',
            layer_group_id: 'group_glebas',
            status: 'active',
            feature_count: 0,
            is_visible: true,
            is_selectable: true,
            is_editable: true,
            opacity: 0.7,
            display_order: 0,
            created_by: 'admin_super',
            created_at: '2024-07-12T10:00:00Z'
        }
    ];
}

// ================================================
// TREE MANAGEMENT
// ================================================

function updateLayerTree() {
    /**Atualizar árvore de camadas*/
    const treeData = buildTreeData();
    
    $('#layer-tree').jstree(true).settings.core.data = treeData;
    $('#layer-tree').jstree(true).refresh();
}

function buildTreeData() {
    /**Construir dados da árvore*/
    const treeData = [];
    
    // Adicionar grupos raiz
    const rootGroups = layerGroups.filter(g => !g.parent_group_id);
    rootGroups.sort((a, b) => a.display_order - b.display_order);
    
    rootGroups.forEach(group => {
        treeData.push(buildGroupNode(group));
    });
    
    // Adicionar camadas sem grupo
    const orphanLayers = layers.filter(l => !l.layer_group_id);
    orphanLayers.sort((a, b) => a.display_order - b.display_order);
    
    orphanLayers.forEach(layer => {
        treeData.push(buildLayerNode(layer));
    });
    
    return treeData;
}

function buildGroupNode(group) {
    /**Construir nó de grupo*/
    const children = [];
    
    // Adicionar subgrupos
    const subGroups = layerGroups.filter(g => g.parent_group_id === group.id);
    subGroups.sort((a, b) => a.display_order - b.display_order);
    subGroups.forEach(subGroup => {
        children.push(buildGroupNode(subGroup));
    });
    
    // Adicionar camadas do grupo
    const groupLayers = layers.filter(l => l.layer_group_id === group.id);
    groupLayers.sort((a, b) => a.display_order - b.display_order);
    groupLayers.forEach(layer => {
        children.push(buildLayerNode(layer));
    });
    
    return {
        id: group.id,
        text: buildGroupText(group),
        type: 'group',
        state: {
            opened: group.is_expanded,
            disabled: false
        },
        children: children,
        data: {
            type: 'group',
            item: group
        }
    };
}

function buildLayerNode(layer) {
    /**Construir nó de camada*/
    return {
        id: layer.id,
        text: buildLayerText(layer),
        type: 'layer',
        state: {
            disabled: false
        },
        data: {
            type: 'layer',
            item: layer
        }
    };
}

function buildGroupText(group) {
    /**Construir texto do grupo*/
    const visibilityIcon = group.is_visible ? 
        '<i class="fas fa-eye layer-visibility-toggle" title="Ocultar grupo"></i>' :
        '<i class="fas fa-eye-slash layer-visibility-toggle hidden" title="Mostrar grupo"></i>';
    
    const statusIcon = getGroupStatusIcon(group);
    
    return `
        <div class="d-flex align-items-center justify-content-between w-100">
            <span>
                ${statusIcon}
                <strong>${group.name}</strong>
                <small class="text-muted">(${getGroupLayerCount(group)} camadas)</small>
            </span>
            <span class="layer-actions">
                ${visibilityIcon}
            </span>
        </div>
    `;
}

function buildLayerText(layer) {
    /**Construir texto da camada*/
    const visibilityIcon = layer.is_visible ? 
        '<i class="fas fa-eye layer-visibility-toggle" title="Ocultar camada"></i>' :
        '<i class="fas fa-eye-slash layer-visibility-toggle hidden" title="Mostrar camada"></i>';
    
    const statusIcon = getLayerStatusIcon(layer);
    const typeIcon = getLayerTypeIcon(layer);
    
    return `
        <div class="d-flex align-items-center justify-content-between w-100">
            <span>
                <span class="layer-status status-${layer.status}"></span>
                <i class="${typeIcon} layer-type-icon"></i>
                ${layer.display_name}
                <small class="text-muted">(${layer.feature_count})</small>
            </span>
            <span class="layer-actions">
                ${visibilityIcon}
                <i class="fas fa-cog" title="Configurações"></i>
            </span>
        </div>
    `;
}

function getGroupStatusIcon(group) {
    /**Obter ícone de status do grupo*/
    return '<i class="fas fa-folder"></i>';
}

function getLayerStatusIcon(layer) {
    /**Obter ícone de status da camada*/
    const icons = {
        'active': 'fas fa-check-circle text-success',
        'hidden': 'fas fa-eye-slash text-warning',
        'archived': 'fas fa-archive text-secondary',
        'deleted': 'fas fa-trash text-danger'
    };
    return `<i class="${icons[layer.status] || icons.active}"></i>`;
}

function getLayerTypeIcon(layer) {
    /**Obter ícone do tipo de camada*/
    const icons = {
        'vector': 'fas fa-vector-square',
        'raster': 'fas fa-image',
        'wms': 'fas fa-globe',
        'wfs': 'fas fa-server',
        'geojson': 'fas fa-file-code',
        'tile': 'fas fa-th'
    };
    return icons[layer.layer_type] || icons.vector;
}

function getGroupLayerCount(group) {
    /**Contar camadas em um grupo*/
    let count = layers.filter(l => l.layer_group_id === group.id).length;
    
    // Adicionar camadas de subgrupos recursivamente
    const subGroups = layerGroups.filter(g => g.parent_group_id === group.id);
    subGroups.forEach(subGroup => {
        count += getGroupLayerCount(subGroup);
    });
    
    return count;
}

// ================================================
// EVENT HANDLERS
// ================================================

function onNodeSelect(node) {
    /**Lidar com seleção de nó*/
    const data = node.data;
    
    if (data.type === 'layer') {
        showLayerDetails(data.item);
    } else if (data.type === 'group') {
        showGroupDetails(data.item);
    }
}

function onNodeMove(data) {
    /**Lidar com movimento de nó*/
    const node = data.node;
    const parent = data.parent;
    const position = data.position;
    
    console.log('Movendo nó:', node.id, 'para:', parent, 'posição:', position);
    
    // TODO: Implementar API para mover camadas/grupos
    showToast('Funcionalidade de reordenação será implementada em breve', 'info');
}

function showLayerDetails(layer) {
    /**Mostrar detalhes da camada*/
    currentLayer = layer;
    
    // Esconder painel de boas-vindas
    document.getElementById('welcome-panel').style.display = 'none';
    
    // Mostrar painel de detalhes
    const detailsPanel = document.getElementById('layer-details-panel');
    detailsPanel.style.display = 'block';
    
    // Atualizar título
    document.getElementById('layer-details-title').innerHTML = 
        `<i class="${getLayerTypeIcon(layer)}"></i> ${layer.display_name}`;
    
    // Preencher formulário
    fillLayerForm(layer);
    
    // Carregar estatísticas
    loadLayerStatistics(layer.id);
    
    // Carregar versões
    loadLayerVersions(layer.id);
}

function fillLayerForm(layer) {
    /**Preencher formulário da camada*/
    document.getElementById('layer-name').value = layer.name || '';
    document.getElementById('layer-display-name').value = layer.display_name || '';
    document.getElementById('layer-description').value = layer.description || '';
    document.getElementById('layer-type').value = layer.layer_type || 'vector';
    document.getElementById('layer-geometry-type').value = layer.geometry_type || 'Polygon';
    document.getElementById('layer-group').value = layer.layer_group_id || '';
    document.getElementById('layer-status').value = layer.status || 'active';
    document.getElementById('layer-display-order').value = layer.display_order || 0;
    document.getElementById('layer-visible').checked = layer.is_visible !== false;
    document.getElementById('layer-selectable').checked = layer.is_selectable !== false;
    document.getElementById('layer-editable').checked = layer.is_editable !== false;
    document.getElementById('layer-public').checked = layer.is_public === true;
    document.getElementById('layer-deletable').checked = layer.is_deletable !== false;
    
    // Estilo
    document.getElementById('layer-opacity').value = layer.opacity || 1;
    document.getElementById('opacity-value').textContent = Math.round((layer.opacity || 1) * 100) + '%';
    document.getElementById('layer-min-zoom').value = layer.min_zoom || 0;
    document.getElementById('layer-max-zoom').value = layer.max_zoom || 18;
    document.getElementById('layer-style-json').value = JSON.stringify(layer.default_style || {}, null, 2);
    
    // Permissões
    document.getElementById('layer-edit-permissions').value = JSON.stringify(layer.edit_permissions || {}, null, 2);
}

async function loadLayerStatistics(layerId) {
    /**Carregar estatísticas da camada*/
    try {
        // Mock statistics
        const stats = {
            total_features: currentLayer.feature_count || 0,
            active_features: currentLayer.feature_count || 0,
            deleted_features: 0,
            geometry_types: {
                [currentLayer.geometry_type]: currentLayer.feature_count || 0
            },
            last_updated: currentLayer.updated_at || currentLayer.created_at,
            file_size_bytes: Math.random() * 1000000,
            version_count: Math.floor(Math.random() * 5) + 1
        };
        
        displayLayerStatistics(stats);
        
    } catch (error) {
        console.error('Erro carregando estatísticas:', error);
    }
}

function displayLayerStatistics(stats) {
    /**Exibir estatísticas da camada*/
    const container = document.getElementById('layer-statistics');
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="statistics-card">
                    <h6><i class="fas fa-shapes"></i> Features</h6>
                    <div class="d-flex justify-content-between">
                        <span>Total:</span>
                        <span class="stat-number">${stats.total_features}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Ativas:</span>
                        <span class="stat-number">${stats.active_features}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Deletadas:</span>
                        <span class="stat-number">${stats.deleted_features}</span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="statistics-card">
                    <h6><i class="fas fa-info-circle"></i> Informações</h6>
                    <div class="d-flex justify-content-between">
                        <span>Tamanho:</span>
                        <span class="stat-number">${formatFileSize(stats.file_size_bytes)}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Versões:</span>
                        <span class="stat-number">${stats.version_count}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Atualizada:</span>
                        <span class="stat-number">${formatDate(stats.last_updated)}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <h6><i class="fas fa-chart-pie"></i> Tipos de Geometria</h6>
            <div class="statistics-card">
                ${Object.entries(stats.geometry_types).map(([type, count]) => `
                    <div class="d-flex justify-content-between">
                        <span>${type}:</span>
                        <span class="stat-number">${count}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

async function loadLayerVersions(layerId) {
    /**Carregar versões da camada*/
    try {
        // Mock versions
        const versions = [
            {
                id: 'v1',
                version_number: 1,
                version_name: 'Versão Inicial',
                description: 'Versão inicial da camada',
                feature_count: currentLayer.feature_count,
                created_by: 'admin_super',
                created_at: currentLayer.created_at
            }
        ];
        
        displayLayerVersions(versions);
        
    } catch (error) {
        console.error('Erro carregando versões:', error);
    }
}

function displayLayerVersions(versions) {
    /**Exibir versões da camada*/
    const container = document.getElementById('layer-versions-list');
    
    if (versions.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhuma versão encontrada</p>';
        return;
    }
    
    container.innerHTML = versions.map(version => `
        <div class="glass-card">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6>
                        <span class="version-badge">v${version.version_number}</span>
                        ${version.version_name}
                    </h6>
                    <small class="text-muted">${version.description || 'Sem descrição'}</small>
                </div>
                <div class="text-end">
                    <small class="text-muted">
                        ${formatDate(version.created_at)}<br>
                        ${version.feature_count} features
                    </small>
                </div>
            </div>
        </div>
    `).join('');
}

// ================================================
// LAYER OPERATIONS
// ================================================

async function saveLayerChanges() {
    /**Salvar alterações da camada*/
    if (!currentLayer) return;
    
    try {
        showLoading(true);
        
        const formData = collectLayerFormData();
        
        // Mock API call
        console.log('Salvando camada:', currentLayer.id, formData);
        
        // Simular delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Atualizar objeto local
        Object.assign(currentLayer, formData);
        
        // Atualizar árvore
        updateLayerTree();
        
        showToast('Alterações salvas com sucesso', 'success');
        
    } catch (error) {
        console.error('Erro salvando camada:', error);
        showToast('Erro ao salvar alterações', 'error');
    } finally {
        showLoading(false);
    }
}

function collectLayerFormData() {
    /**Coletar dados do formulário*/
    return {
        display_name: document.getElementById('layer-display-name').value,
        description: document.getElementById('layer-description').value,
        layer_group_id: document.getElementById('layer-group').value || null,
        status: document.getElementById('layer-status').value,
        display_order: parseInt(document.getElementById('layer-display-order').value) || 0,
        is_visible: document.getElementById('layer-visible').checked,
        is_selectable: document.getElementById('layer-selectable').checked,
        is_editable: document.getElementById('layer-editable').checked,
        is_public: document.getElementById('layer-public').checked,
        is_deletable: document.getElementById('layer-deletable').checked,
        opacity: parseFloat(document.getElementById('layer-opacity').value),
        min_zoom: parseInt(document.getElementById('layer-min-zoom').value),
        max_zoom: parseInt(document.getElementById('layer-max-zoom').value)
    };
}

async function createLayer() {
    /**Criar nova camada*/
    try {
        showLoading(true);
        
        const formData = {
            name: document.getElementById('new-layer-name').value,
            display_name: document.getElementById('new-layer-display-name').value,
            description: document.getElementById('new-layer-description').value,
            layer_type: document.getElementById('new-layer-type').value,
            geometry_type: document.getElementById('new-layer-geometry-type').value,
            layer_group_id: document.getElementById('new-layer-group').value || null,
            display_order: parseInt(document.getElementById('new-layer-display-order').value) || 0
        };
        
        // Validações
        if (!formData.name || !formData.display_name) {
            throw new Error('Nome e nome de exibição são obrigatórios');
        }
        
        // Mock API call
        console.log('Criando camada:', formData);
        
        // Simular delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Criar objeto mock
        const newLayer = {
            id: `layer_${Date.now()}`,
            ...formData,
            status: 'active',
            feature_count: 0,
            is_visible: true,
            is_selectable: true,
            is_editable: true,
            opacity: 1.0,
            created_by: 'admin_super',
            created_at: new Date().toISOString()
        };
        
        // Adicionar à lista
        layers.push(newLayer);
        
        // Atualizar árvore
        updateLayerTree();
        
        // Fechar modal
        bootstrap.Modal.getInstance(document.getElementById('createLayerModal')).hide();
        
        // Limpar formulário
        document.getElementById('create-layer-form').reset();
        
        showToast('Camada criada com sucesso', 'success');
        
    } catch (error) {
        console.error('Erro criando camada:', error);
        showToast(error.message || 'Erro ao criar camada', 'error');
    } finally {
        showLoading(false);
    }
}

async function createGroup() {
    /**Criar novo grupo*/
    try {
        showLoading(true);
        
        const formData = {
            name: document.getElementById('new-group-name').value,
            description: document.getElementById('new-group-description').value,
            parent_group_id: document.getElementById('new-group-parent').value || null,
            display_order: parseInt(document.getElementById('new-group-display-order').value) || 0
        };
        
        // Validações
        if (!formData.name) {
            throw new Error('Nome do grupo é obrigatório');
        }
        
        // Mock API call
        console.log('Criando grupo:', formData);
        
        // Simular delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Criar objeto mock
        const newGroup = {
            id: `group_${Date.now()}`,
            ...formData,
            is_expanded: true,
            is_visible: true,
            children: [],
            layers: []
        };
        
        // Adicionar à lista
        layerGroups.push(newGroup);
        
        // Atualizar árvore e dropdowns
        updateLayerTree();
        updateGroupDropdowns();
        
        // Fechar modal
        bootstrap.Modal.getInstance(document.getElementById('createGroupModal')).hide();
        
        // Limpar formulário
        document.getElementById('create-group-form').reset();
        
        showToast('Grupo criado com sucesso', 'success');
        
    } catch (error) {
        console.error('Erro criando grupo:', error);
        showToast(error.message || 'Erro ao criar grupo', 'error');
    } finally {
        showLoading(false);
    }
}

// ================================================
// UI HELPERS
// ================================================

function updateGroupDropdowns() {
    /**Atualizar dropdowns de grupos*/
    const selects = [
        'layer-group',
        'new-layer-group', 
        'new-group-parent'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // Manter valor atual
        const currentValue = select.value;
        
        // Limpar opções
        const firstOption = select.querySelector('option');
        select.innerHTML = '';
        
        // Adicionar primeira opção
        if (firstOption) {
            select.appendChild(firstOption.cloneNode(true));
        }
        
        // Adicionar grupos
        layerGroups.forEach(group => {
            const option = document.createElement('option');
            option.value = group.id;
            option.textContent = group.name;
            select.appendChild(option);
        });
        
        // Restaurar valor
        if (currentValue) {
            select.value = currentValue;
        }
    });
}

function updateStatistics() {
    /**Atualizar estatísticas rápidas*/
    const activeLayers = layers.filter(l => l.status === 'active').length;
    const totalFeatures = layers.reduce((sum, l) => sum + (l.feature_count || 0), 0);
    const totalGroups = layerGroups.length;
    
    document.getElementById('stat-active-layers').textContent = activeLayers;
    document.getElementById('stat-total-features').textContent = totalFeatures.toLocaleString();
    document.getElementById('stat-total-groups').textContent = totalGroups;
}

function filterLayers() {
    /**Filtrar camadas*/
    const searchTerm = document.getElementById('layer-search').value.toLowerCase();
    const typeFilter = document.getElementById('filter-type').value;
    const statusFilter = document.getElementById('filter-status').value;
    
    // TODO: Implementar filtro na árvore
    console.log('Filtrando:', { searchTerm, typeFilter, statusFilter });
}

function showToast(message, type = 'info') {
    /**Mostrar toast*/
    const toastContainer = document.getElementById('toast-container');
    const toastId = 'toast_' + Date.now();
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                <strong class="me-auto">${getToastTitle(type)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remover após ocultar
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || icons.info;
}

function getToastTitle(type) {
    const titles = {
        'success': 'Sucesso',
        'error': 'Erro',
        'warning': 'Aviso',
        'info': 'Informação'
    };
    return titles[type] || titles.info;
}

function showLoading(show) {
    /**Mostrar/ocultar loading*/
    // TODO: Implementar loading overlay
    console.log('Loading:', show);
}

function formatFileSize(bytes) {
    /**Formatar tamanho de arquivo*/
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    /**Formatar data*/
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait) {
    /**Debounce function*/
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ================================================
// PUBLIC FUNCTIONS (called from HTML)
// ================================================

function refreshLayers() {
    /**Atualizar camadas*/
    loadLayerData();
}

function showCreateLayerModal() {
    /**Mostrar modal de criação de camada*/
    const modal = new bootstrap.Modal(document.getElementById('createLayerModal'));
    modal.show();
}

function showCreateGroupModal() {
    /**Mostrar modal de criação de grupo*/
    const modal = new bootstrap.Modal(document.getElementById('createGroupModal'));
    modal.show();
}

function expandAllGroups() {
    /**Expandir todos os grupos*/
    $('#layer-tree').jstree('open_all');
}

function collapseAllGroups() {
    /**Recolher todos os grupos*/
    $('#layer-tree').jstree('close_all');
}

function closeLayerDetails() {
    /**Fechar detalhes da camada*/
    document.getElementById('layer-details-panel').style.display = 'none';
    document.getElementById('welcome-panel').style.display = 'flex';
    currentLayer = null;
}

function resetLayerForm() {
    /**Resetar formulário da camada*/
    if (currentLayer) {
        fillLayerForm(currentLayer);
    }
}

function autoSaveLayer() {
    /**Auto-salvar camada*/
    if (currentLayer) {
        saveLayerChanges();
    }
}

function updateLayerStyle() {
    /**Atualizar estilo da camada*/
    // TODO: Implementar atualização de estilo
    showToast('Estilo atualizado', 'success');
}

function updateLayerPermissions() {
    /**Atualizar permissões da camada*/
    // TODO: Implementar atualização de permissões
    showToast('Permissões atualizadas', 'success');
}

function createLayerVersion() {
    /**Criar nova versão da camada*/
    // TODO: Implementar criação de versão
    showToast('Nova versão criada', 'success');
}

function exportLayerData() {
    /**Exportar dados da camada*/
    // TODO: Implementar exportação
    showToast('Exportação iniciada', 'info');
}

function validateLayerData() {
    /**Validar dados da camada*/
    // TODO: Implementar validação
    showToast('Dados validados com sucesso', 'success');
}

function refreshLayerData() {
    /**Atualizar dados da camada*/
    if (currentLayer) {
        loadLayerStatistics(currentLayer.id);
        showToast('Dados atualizados', 'success');
    }
}

// Context menu functions
function getContextMenuItems(node) {
    /**Obter itens do menu de contexto*/
    const items = {};
    
    if (node.data.type === 'layer') {
        items.edit = {
            label: "Editar",
            icon: "fas fa-edit",
            action: () => showLayerDetails(node.data.item)
        };
        items.duplicate = {
            label: "Duplicar",
            icon: "fas fa-copy",
            action: () => console.log('Duplicar camada')
        };
        items.export = {
            label: "Exportar",
            icon: "fas fa-download",
            action: () => exportLayerData()
        };
        items.sep1 = "---------";
        items.delete = {
            label: "Deletar",
            icon: "fas fa-trash",
            action: () => console.log('Deletar camada')
        };
    } else if (node.data.type === 'group') {
        items.addLayer = {
            label: "Adicionar Camada",
            icon: "fas fa-plus",
            action: () => showCreateLayerModal()
        };
        items.addGroup = {
            label: "Adicionar Subgrupo",
            icon: "fas fa-folder-plus",
            action: () => showCreateGroupModal()
        };
        items.sep1 = "---------";
        items.edit = {
            label: "Editar",
            icon: "fas fa-edit",
            action: () => console.log('Editar grupo')
        };
        items.delete = {
            label: "Deletar",
            icon: "fas fa-trash",
            action: () => console.log('Deletar grupo')
        };
    }
    
    return items;
}

function editSelectedItem() {
    console.log('Editar item selecionado');
}

function duplicateSelectedItem() {
    console.log('Duplicar item selecionado');
}

function exportSelectedItem() {
    console.log('Exportar item selecionado');
}

function deleteSelectedItem() {
    console.log('Deletar item selecionado');
}

function hideContextMenu() {
    document.getElementById('context-menu').style.display = 'none';
}