/**
 * Geojson.io Style Interface Implementation
 * Implements the geojson.io-like interface with sidebar toolbar, modal editing, and table view
 */

class GeojsonStyleInterface {
    constructor() {
        this.map = null;
        this.drawnItems = null;
        this.drawControls = {};
        this.currentTool = 'pan';
        this.selectedFeature = null;
        this.features = new Map();
        this.baseLayers = {};
        this.currentBaseLayer = 'osm';
        
        this.init();
    }

    init() {
        this.waitForMap();
        this.setupEventListeners();
    }

    waitForMap() {
        // Primeiro, tentar encontrar o mapa existente
        if (typeof window.map !== 'undefined' && window.map) {
            this.map = window.map;
            this.drawnItems = window.drawnItems || new L.FeatureGroup();
            if (!window.drawnItems) {
                window.drawnItems = this.drawnItems;
                this.map.addLayer(this.drawnItems);
            }
            this.setupDrawingTools();
            return;
        }

        // Se não encontrar, criar um novo mapa
        const mapElement = document.getElementById('map');
        if (mapElement && !mapElement._leaflet_id) {
            this.initNewMap();
        } else if (mapElement && mapElement._leaflet_id) {
            // Mapa já existe, mas não está nas variáveis globais
            this.map = mapElement._leaflet_map || mapElement._map;
            this.drawnItems = new L.FeatureGroup();
            window.drawnItems = this.drawnItems;
            this.map.addLayer(this.drawnItems);
            this.setupDrawingTools();
        } else {
            setTimeout(() => this.waitForMap(), 200);
        }
    }

    initNewMap() {
        try {
            console.log('🗺️ Inicializando novo mapa...');
            
            const mapElement = document.getElementById('map');
            if (!mapElement) {
                console.error('❌ Elemento #map não encontrado');
                return;
            }

            // Criar o mapa
            this.map = L.map('map').setView([-2.5297, -44.3028], 13);

            // Configurar camadas base
            this.setupBaseLayers();

            // Criar grupo de elementos desenhados
            this.drawnItems = new L.FeatureGroup();
            this.map.addLayer(this.drawnItems);

            // Configurar ferramentas de desenho
            this.setupDrawingTools();

            // Tornar disponível globalmente
            window.map = this.map;
            window.drawnItems = this.drawnItems;

            console.log('✅ Mapa inicializado com sucesso');

            // Disparar evento personalizado
            document.dispatchEvent(new CustomEvent('mapReady', {
                detail: { map: this.map, drawnItems: this.drawnItems }
            }));

        } catch (error) {
            console.error('❌ Erro ao inicializar mapa:', error);
        }
    }

    setupEventListeners() {
        // Toolbar buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('geojson-btn') || e.target.closest('.geojson-btn')) {
                const btn = e.target.classList.contains('geojson-btn') ? e.target : e.target.closest('.geojson-btn');
                this.handleToolbarClick(btn);
            }
        });

        // Modal events
        this.setupModalEvents();
        
        // Feature events
        this.setupFeatureEvents();
    }

    setupModalEvents() {
        // Geojson modal
        const geojsonModal = document.getElementById('geojson-modal');
        const geojsonModalClose = document.getElementById('geojson-modal-close');
        const cancelBtn = document.getElementById('cancel-feature-btn');
        const saveBtn = document.getElementById('save-feature-btn');
        const deleteBtn = document.getElementById('delete-feature-btn');

        if (geojsonModalClose) {
            geojsonModalClose.addEventListener('click', () => this.closeModal());
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeModal());
        }
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveFeature());
        }
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteFeature());
        }

        // Tab switching
        document.querySelectorAll('.geojson-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Property management
        const addPropertyBtn = document.getElementById('add-property-btn');
        const addSimplestyleBtn = document.getElementById('add-simplestyle-btn');
        
        if (addPropertyBtn) {
            addPropertyBtn.addEventListener('click', () => this.addProperty());
        }
        if (addSimplestyleBtn) {
            addSimplestyleBtn.addEventListener('click', () => this.openStyleModal());
        }
        
        // Style modal events
        this.setupStyleModalEvents();

        // Table modal
        const tableModal = document.getElementById('table-modal');
        const tableModalClose = document.getElementById('table-modal-close');
        
        if (tableModalClose) {
            tableModalClose.addEventListener('click', () => this.closeTableModal());
        }

        // Close modals on backdrop click
        if (geojsonModal) {
            geojsonModal.addEventListener('click', (e) => {
                if (e.target === geojsonModal) this.closeModal();
            });
        }
        if (tableModal) {
            tableModal.addEventListener('click', (e) => {
                if (e.target === tableModal) this.closeTableModal();
            });
        }
    }

    setupFeatureEvents() {
        // Wait for drawnItems to be available
        const setupEvents = () => {
            if (this.drawnItems) {
                // Event for clicking on existing features
                this.drawnItems.on('click', (e) => {
                    console.log('🖱️ Clique em feature detectado');
                    e.originalEvent.preventDefault();
                    e.originalEvent.stopPropagation();
                    this.selectFeature(e.layer);
                });
                
                // Event for newly created features
                this.map.on('draw:created', (e) => {
                    console.log('🆕 Feature criado:', e.layerType);
                    this.onFeatureCreated(e);
                });
                
                // Event for map clicks (close modal if clicking empty area)
                this.map.on('click', (e) => {
                    // Only close modal if not clicking on a feature
                    if (!e.originalEvent.defaultPrevented) {
                        this.closeModal();
                    }
                });
                
                // Additional event to catch feature clicks from any layer
                this.map.on('layeradd', (e) => {
                    if (e.layer && e.layer.on) {
                        e.layer.on('click', (clickEvent) => {
                            console.log('🖱️ Clique direto na layer');
                            clickEvent.originalEvent.preventDefault();
                            clickEvent.originalEvent.stopPropagation();
                            this.selectFeature(e.layer);
                        });
                    }
                });
                
                console.log('✅ Eventos de feature configurados');
            } else {
                setTimeout(setupEvents, 100);
            }
        };
        setupEvents();
    }
    
    // Method to add imported features to the geojson interface
    addImportedFeature(layer, properties = {}) {
        const featureId = this.generateFeatureId();
        
        // Add feature to drawnItems
        this.drawnItems.addLayer(layer);
        
        // Determine layer type
        let layerType = 'polygon';
        if (layer instanceof L.Marker) {
            layerType = 'marker';
        } else if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
            layerType = 'polyline';
        } else if (layer instanceof L.Polygon) {
            layerType = 'polygon';
        } else if (layer instanceof L.Circle) {
            layerType = 'circle';
        }
        
        // Store feature data
        const featureData = {
            id: featureId,
            type: layerType,
            layer: layer,
            properties: properties || {},
            geometry: layer.toGeoJSON().geometry
        };
        
        layer._featureId = featureId;
        layer.feature = {
            type: 'Feature',
            properties: featureData.properties,
            geometry: featureData.geometry
        };
        
        // Add click event to the imported layer
        layer.on('click', (e) => {
            console.log('🔄 Clique em feature importada:', featureId);
            e.originalEvent.preventDefault();
            e.originalEvent.stopPropagation();
            this.selectFeature(layer);
        });
        
        this.features.set(featureId, featureData);
        
        // Update layer panel
        this.updateLayersPanel();
        
        console.log('📥 Feature importada adicionada:', featureId, layerType);
        
        return featureId;
    }
    
    setupBaseLayers() {
        // OpenStreetMap
        this.baseLayers.osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        });
        
        // Google Satellite
        this.baseLayers.satellite = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            attribution: '© Google',
            maxZoom: 20
        });
        
        // Adicionar camada padrão
        this.baseLayers[this.currentBaseLayer].addTo(this.map);
        
        console.log('🗺️ Camadas base configuradas');
    }
    
    toggleBaseMap() {
        // Remover camada atual
        this.map.removeLayer(this.baseLayers[this.currentBaseLayer]);
        
        // Alternar entre as camadas
        if (this.currentBaseLayer === 'osm') {
            this.currentBaseLayer = 'satellite';
            console.log('🛰️ Mudando para vista satélite');
        } else {
            this.currentBaseLayer = 'osm';
            console.log('🗺️ Mudando para OpenStreetMap');
        }
        
        // Adicionar nova camada
        this.baseLayers[this.currentBaseLayer].addTo(this.map);
        
        // Atualizar visual do botão
        const btn = document.getElementById('toggle-basemap');
        if (btn) {
            const icon = btn.querySelector('i');
            if (this.currentBaseLayer === 'satellite') {
                icon.className = 'fas fa-satellite';
                btn.title = 'Switch to Street Map';
            } else {
                icon.className = 'fas fa-map';
                btn.title = 'Switch to Satellite';
            }
        }
    }

    setupDrawingTools() {
        if (!this.map || !L.Control.Draw) return;

        // Clear existing controls
        this.map.eachLayer((layer) => {
            if (layer instanceof L.Control.Draw) {
                this.map.removeControl(layer);
            }
        });

        // Setup individual drawing controls
        this.drawControls = {
            marker: new L.Draw.Marker(this.map, {
                icon: new L.Icon({
                    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
                    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }),
            polyline: new L.Draw.Polyline(this.map, {
                shapeOptions: {
                    color: '#3b82f6',
                    weight: 3,
                    opacity: 0.8
                }
            }),
            polygon: new L.Draw.Polygon(this.map, {
                shapeOptions: {
                    color: '#3b82f6',
                    fillColor: '#3b82f6',
                    fillOpacity: 0.2,
                    weight: 2
                }
            }),
            rectangle: new L.Draw.Rectangle(this.map, {
                shapeOptions: {
                    color: '#3b82f6',
                    fillColor: '#3b82f6',
                    fillOpacity: 0.2,
                    weight: 2
                }
            }),
            circle: new L.Draw.Circle(this.map, {
                shapeOptions: {
                    color: '#3b82f6',
                    fillColor: '#3b82f6',
                    fillOpacity: 0.2,
                    weight: 2
                }
            })
        };
    }

    handleToolbarClick(btn) {
        const tool = btn.dataset.tool || btn.id.replace(/^(zoom-|pan-|draw-|edit-|delete-)/, '');
        
        // Update active state
        document.querySelectorAll('.geojson-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Disable all drawing tools
        Object.values(this.drawControls).forEach(control => {
            if (control.disable) control.disable();
        });

        // Handle different tools
        switch (btn.id) {
            case 'zoom-in':
                this.map.zoomIn();
                break;
            case 'zoom-out':
                this.map.zoomOut();
                break;
            case 'pan-mode':
                this.currentTool = 'pan';
                this.map.dragging.enable();
                break;
            case 'locate-me':
                this.locateUser();
                break;
            case 'table-view':
                this.openTableView();
                break;
            case 'save-data':
                this.saveAllData();
                break;
            case 'toggle-basemap':
                this.toggleBaseMap();
                break;
            case 'edit-mode':
                this.enableEditMode();
                break;
            case 'delete-mode':
                this.enableDeleteMode();
                break;
            default:
                if (tool && this.drawControls[tool]) {
                    this.enableDrawingTool(tool);
                }
        }
    }

    enableDrawingTool(tool) {
        this.currentTool = tool;
        if (this.drawControls[tool]) {
            this.drawControls[tool].enable();
        }
    }

    enableEditMode() {
        this.currentTool = 'edit';
        // TODO: Implement edit mode
        console.log('Edit mode enabled');
    }

    enableDeleteMode() {
        this.currentTool = 'delete';
        // TODO: Implement delete mode
        console.log('Delete mode enabled');
    }

    locateUser() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                this.map.setView([lat, lng], 16);
                
                // Add a temporary marker
                const marker = L.marker([lat, lng]).addTo(this.map);
                setTimeout(() => {
                    this.map.removeLayer(marker);
                }, 3000);
            }, (error) => {
                console.error('Geolocation error:', error);
                alert('Unable to get your location');
            });
        } else {
            alert('Geolocation is not supported by this browser');
        }
    }

    onFeatureCreated(e) {
        const layer = e.layer;
        const featureId = this.generateFeatureId();
        
        // Add feature to drawnItems
        this.drawnItems.addLayer(layer);
        
        // Store feature data
        const featureData = {
            id: featureId,
            type: e.layerType,
            layer: layer,
            properties: {
                nome_gleba: `${this.capitalizeFirst(e.layerType)} ${this.features.size + 1}`,
                no_gleba: (this.features.size + 1).toString().padStart(3, '0')
            },
            geometry: layer.toGeoJSON().geometry
        };
        
        layer._featureId = featureId;
        layer.feature = {
            type: 'Feature',
            properties: featureData.properties,
            geometry: featureData.geometry
        };
        
        // Add click event to the new layer
        layer.on('click', (e) => {
            console.log('🖱️ Clique na feature criada:', featureId);
            e.originalEvent.preventDefault();
            e.originalEvent.stopPropagation();
            this.selectFeature(layer);
        });
        
        this.features.set(featureId, featureData);
        
        // Update layer panel using existing system
        this.updateLayersPanel();
        
        // Reset to pan mode after creating feature
        this.resetToPanMode();
        
        // Auto-open modal for new features
        this.selectFeature(layer);
    }

    updateLayersPanel() {
        // Try to use existing layer management functions
        if (typeof window.updateLayersList === 'function') {
            window.updateLayersList();
        } else if (typeof updateLayersList === 'function') {
            updateLayersList();
        } else {
            // Create layer entry manually
            this.createLayerPanelEntry();
        }
    }

    createLayerPanelEntry() {
        const layerControls = document.getElementById('layer-controls');
        if (!layerControls) return;

        // Clear and rebuild layer list
        layerControls.innerHTML = '';
        
        let index = 1;
        this.features.forEach((feature, id) => {
            const layerDiv = document.createElement('div');
            layerDiv.className = 'layer-item';
            layerDiv.innerHTML = `
                <div class="layer-info">
                    <span class="layer-icon">
                        <i class="fas fa-${this.getLayerIcon(feature.type)}"></i>
                    </span>
                    <div class="layer-details">
                        <h6>${feature.properties.nome_gleba || `${this.capitalizeFirst(feature.type)} ${index}`}</h6>
                        <p>POLÍGONO</p>
                    </div>
                </div>
                <div class="layer-controls">
                    <label class="switch">
                        <input type="checkbox" checked onchange="window.geojsonInterface.toggleLayerVisibility('${id}', this.checked)">
                        <span class="slider"></span>
                    </label>
                    <button class="btn-layer-info" onclick="window.geojsonInterface.zoomToFeature('${id}')">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="btn-layer-edit" onclick="window.geojsonInterface.editFeatureById('${id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            `;
            
            layerControls.appendChild(layerDiv);
            index++;
        });
    }

    getLayerIcon(type) {
        const icons = {
            'marker': 'map-marker-alt',
            'polyline': 'project-diagram',
            'polygon': 'draw-polygon',
            'rectangle': 'square',
            'circle': 'circle'
        };
        return icons[type] || 'map-marked-alt';
    }

    toggleLayerVisibility(featureId, visible) {
        const feature = this.features.get(featureId);
        if (feature && feature.layer) {
            if (visible) {
                if (!this.drawnItems.hasLayer(feature.layer)) {
                    this.drawnItems.addLayer(feature.layer);
                }
            } else {
                this.drawnItems.removeLayer(feature.layer);
            }
        }
    }

    showLayerInfo(featureId) {
        const feature = this.features.get(featureId);
        if (feature && feature.layer) {
            // Fazer zoom para a extensão da feature
            if (feature.layer.getBounds && typeof feature.layer.getBounds === 'function') {
                // Para polígonos e linhas
                this.map.fitBounds(feature.layer.getBounds(), {
                    padding: [20, 20],
                    maxZoom: 19
                });
            } else if (feature.layer.getLatLng && typeof feature.layer.getLatLng === 'function') {
                // Para pontos/marcadores
                this.map.setView(feature.layer.getLatLng(), 19);
            }
            
            console.log('🔍 Zoom realizado para feature:', featureId);
        }
    }
    
    zoomToFeature(featureId) {
        // Função separada apenas para zoom
        this.showLayerInfo(featureId);
    }

    editFeatureById(featureId) {
        const feature = this.features.get(featureId);
        if (feature) {
            this.selectedFeature = feature.layer;
            this.openModal(feature.layer);
        }
    }

    selectFeature(layer) {
        console.log('🎯 Selecionando feature:', layer._featureId);
        this.selectedFeature = layer;
        this.openModal(layer);
    }

    openModal(layer) {
        console.log('📂 Tentando abrir modal para feature:', layer._featureId);
        
        const modal = document.getElementById('geojson-modal');
        if (!modal) {
            console.error('❌ Modal geojson não encontrado');
            return;
        }

        const featureId = layer._featureId;
        const featureData = this.features.get(featureId);
        
        if (featureData) {
            console.log('✅ Dados da feature encontrados, populando modal');
            this.populateModal(featureData);
            modal.style.display = 'flex';
            
            // Ensure modal is on top
            modal.style.zIndex = '10000';
            
            console.log('✅ Modal geojson.io aberto');
        } else {
            console.error('❌ Dados da feature não encontrados para ID:', featureId);
        }
    }

    populateModal(featureData) {
        // Populate Dados da Gleba
        this.populateGlebaForm(featureData);
        
        // Populate info tab (Informações Técnicas)
        this.populateInfoTab(featureData);
    }
    
    populateGlebaForm(featureData) {
        const props = featureData.properties || {};
        
        // Informações da Gleba
        this.setFieldValue('gleba-numero', props.no_gleba || props['gleba-numero'] || '');
        this.setFieldValue('gleba-nome', props.nome_gleba || props['gleba-nome'] || featureData.properties.nome_gleba || `${this.capitalizeFirst(featureData.geometry?.type || 'Feature')} ${this.features.size}`);
        
        // Área e Perímetro (calculados automaticamente)
        if (featureData.layer) {
            const area = this.calculateArea(featureData.layer);
            const perimeter = this.calculatePerimeter(featureData.layer);
            this.setFieldValue('gleba-area', area);
            this.setFieldValue('gleba-perimetro', perimeter);
        }
        
        // Informações do Proprietário
        this.setFieldValue('proprietario-nome', props['proprietario-nome'] || props.proprietario || '');
        this.setFieldValue('proprietario-cpf', props['proprietario-cpf'] || props.cpf || '');
        this.setFieldValue('proprietario-rg', props['proprietario-rg'] || props.rg || '');
        
        // Endereço
        this.setFieldValue('endereco-rua', props['endereco-rua'] || props.rua || '');
        this.setFieldValue('endereco-bairro', props['endereco-bairro'] || props.bairro || '');
        this.setFieldValue('endereco-quadra', props['endereco-quadra'] || props.quadra || '');
        this.setFieldValue('endereco-cep', props['endereco-cep'] || props.cep || '');
        this.setFieldValue('endereco-cidade', props['endereco-cidade'] || props.cidade || '');
        this.setFieldValue('endereco-uf', props['endereco-uf'] || props.uf || '');
        
        // Testadas
        this.setFieldValue('testada-frente', props['testada-frente'] || '');
        this.setFieldValue('testada-ld', props['testada-ld'] || '');
        this.setFieldValue('testada-le', props['testada-le'] || '');
        this.setFieldValue('testada-f', props['testada-f'] || '');
        
        // Informações do Imóvel
        this.setFieldValue('imovel-matricula', props['imovel-matricula'] || props.matricula || '');
        this.setFieldValue('zoneamento', props.zoneamento || '');
        this.setFieldValue('finalidade', props.finalidade || '');
        this.setFieldValue('padrao-construtivo', props['padrao-construtivo'] || '');
        this.setFieldValue('situacao-fundiaria', props['situacao-fundiaria'] || '');
        this.setFieldValue('ocupacao-atual', props['ocupacao-atual'] || '');
        this.setFieldValue('descricao-imovel', props['descricao-imovel'] || props.descricao || '');
    }
    
    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value || '';
        }
    }
    
    calculateArea(layer) {
        try {
            if (layer.getLatLngs && (layer instanceof L.Polygon || layer instanceof L.Rectangle)) {
                const area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
                return this.formatArea(area);
            }
        } catch (error) {
            console.warn('Erro ao calcular área:', error);
        }
        return 'N/A';
    }
    
    calculatePerimeter(layer) {
        try {
            if (layer.getLatLngs) {
                let perimeter = 0;
                const coords = layer.getLatLngs()[0] || layer.getLatLngs();
                
                for (let i = 0; i < coords.length; i++) {
                    const nextIndex = (i + 1) % coords.length;
                    perimeter += coords[i].distanceTo(coords[nextIndex]);
                }
                
                return this.formatDistance(perimeter);
            }
        } catch (error) {
            console.warn('Erro ao calcular perímetro:', error);
        }
        return 'N/A';
    }

    populateInfoTab(featureData) {
        const typeSpan = document.getElementById('feature-type-info');
        const areaSpan = document.getElementById('feature-area-info');
        const lengthSpan = document.getElementById('feature-length-info');
        const coordsSpan = document.getElementById('feature-coords-info');

        if (typeSpan) typeSpan.textContent = featureData.type || '-';
        
        // Calculate area/length based on geometry type
        if (featureData.layer) {
            if (featureData.type === 'polygon' || featureData.type === 'rectangle') {
                const area = L.GeometryUtil.geodesicArea(featureData.layer.getLatLngs()[0]);
                if (areaSpan) areaSpan.textContent = this.formatArea(area);
            } else if (featureData.type === 'polyline') {
                // Calculate length for polylines
                const length = this.calculateLength(featureData.layer.getLatLngs());
                if (lengthSpan) lengthSpan.textContent = this.formatDistance(length);
            }
        }

        // Show coordinates (simplified)
        if (coordsSpan && featureData.geometry) {
            const coords = this.simplifyCoordinates(featureData.geometry.coordinates);
            coordsSpan.textContent = coords;
        }
    }

    addProperty(key = '', value = '') {
        this.addPropertyRow(key, value);
    }

    addPropertyRow(key = '', value = '') {
        const propertiesList = document.getElementById('properties-list');
        if (!propertiesList) return;

        const row = document.createElement('div');
        row.className = 'geojson-property-row';
        row.innerHTML = `
            <input type="text" class="geojson-property-key" placeholder="Key" value="${key}">
            <input type="text" class="geojson-property-value" placeholder="Value" value="${value}">
            <button type="button" class="geojson-remove-property" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        propertiesList.appendChild(row);
    }

    setupStyleModalEvents() {
        const styleModal = document.getElementById('style-modal');
        const styleModalClose = document.getElementById('style-modal-close');
        const applyStyleBtn = document.getElementById('apply-style-btn');
        const cancelStyleBtn = document.getElementById('cancel-style-btn');
        
        // Range sliders value updates
        const fillOpacitySlider = document.getElementById('fill-opacity');
        const strokeOpacitySlider = document.getElementById('stroke-opacity');
        const strokeWidthSlider = document.getElementById('stroke-width');
        
        if (fillOpacitySlider) {
            fillOpacitySlider.addEventListener('input', (e) => {
                document.getElementById('fill-opacity-value').textContent = Math.round(e.target.value * 100) + '%';
            });
        }
        
        if (strokeOpacitySlider) {
            strokeOpacitySlider.addEventListener('input', (e) => {
                document.getElementById('stroke-opacity-value').textContent = Math.round(e.target.value * 100) + '%';
            });
        }
        
        if (strokeWidthSlider) {
            strokeWidthSlider.addEventListener('input', (e) => {
                document.getElementById('stroke-width-value').textContent = e.target.value + 'px';
            });
        }
        
        if (styleModalClose) {
            styleModalClose.addEventListener('click', () => this.closeStyleModal());
        }
        if (cancelStyleBtn) {
            cancelStyleBtn.addEventListener('click', () => this.closeStyleModal());
        }
        if (applyStyleBtn) {
            applyStyleBtn.addEventListener('click', () => this.applyStyles());
        }
        
        // Close modal on backdrop click
        if (styleModal) {
            styleModal.addEventListener('click', (e) => {
                if (e.target === styleModal) this.closeStyleModal();
            });
        }
    }
    
    openStyleModal() {
        if (!this.selectedFeature) {
            console.warn('Nenhuma feature selecionada para editar estilos');
            return;
        }
        
        const modal = document.getElementById('style-modal');
        if (!modal) return;
        
        // Populate with current styles if they exist
        const featureId = this.selectedFeature._featureId;
        const featureData = this.features.get(featureId);
        
        if (featureData && featureData.properties) {
            const props = featureData.properties;
            
            // Set current values
            const fillColor = document.getElementById('fill-color');
            const fillOpacity = document.getElementById('fill-opacity');
            const strokeColor = document.getElementById('stroke-color');
            const strokeOpacity = document.getElementById('stroke-opacity');
            const strokeWidth = document.getElementById('stroke-width');
            
            if (fillColor && props.fill) fillColor.value = props.fill;
            if (fillOpacity && props['fill-opacity']) {
                fillOpacity.value = props['fill-opacity'];
                document.getElementById('fill-opacity-value').textContent = Math.round(props['fill-opacity'] * 100) + '%';
            }
            if (strokeColor && props.stroke) strokeColor.value = props.stroke;
            if (strokeOpacity && props['stroke-opacity']) {
                strokeOpacity.value = props['stroke-opacity'];
                document.getElementById('stroke-opacity-value').textContent = Math.round(props['stroke-opacity'] * 100) + '%';
            }
            if (strokeWidth && props['stroke-width']) {
                strokeWidth.value = props['stroke-width'];
                document.getElementById('stroke-width-value').textContent = props['stroke-width'] + 'px';
            }
        }
        
        modal.style.display = 'flex';
        modal.style.zIndex = '10001';
    }
    
    closeStyleModal() {
        const modal = document.getElementById('style-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    applyStyles() {
        if (!this.selectedFeature) return;
        
        const fillColor = document.getElementById('fill-color').value;
        const fillOpacity = document.getElementById('fill-opacity').value;
        const strokeColor = document.getElementById('stroke-color').value;
        const strokeOpacity = document.getElementById('stroke-opacity').value;
        const strokeWidth = document.getElementById('stroke-width').value;
        
        // Create style properties
        const styleProps = {
            'fill': fillColor,
            'fill-opacity': fillOpacity,
            'stroke': strokeColor,
            'stroke-opacity': strokeOpacity,
            'stroke-width': strokeWidth
        };
        
        // Update feature properties
        const featureId = this.selectedFeature._featureId;
        const featureData = this.features.get(featureId);
        
        if (featureData) {
            // Merge style properties with existing properties
            featureData.properties = { ...featureData.properties, ...styleProps };
            this.features.set(featureId, featureData);
            
            // Apply styles to the layer
            this.applySimplestyles(this.selectedFeature, styleProps);
            
            console.log('🎨 Estilos aplicados à feature:', featureId);
        }
        
        this.closeStyleModal();
    }
    
    addSimplestyleProperties() {
        // Deprecated - now using simplified style modal
        this.openStyleModal();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.geojson-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.geojson-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab-content`).classList.add('active');
    }

    saveFeature() {
        if (!this.selectedFeature) return;

        const featureId = this.selectedFeature._featureId;
        const featureData = this.features.get(featureId);
        
        if (featureData) {
            // Collect properties from form
            const properties = {};
            const propertyRows = document.querySelectorAll('.geojson-property-row');
            
            propertyRows.forEach(row => {
                const keyInput = row.querySelector('.geojson-property-key');
                const valueInput = row.querySelector('.geojson-property-value');
                
                if (keyInput.value.trim()) {
                    properties[keyInput.value.trim()] = valueInput.value;
                }
            });

            // Update feature data
            featureData.properties = properties;
            this.features.set(featureId, featureData);

            // Apply styles if simplestyle properties exist
            this.applySimplestyles(this.selectedFeature, properties);
            
            // Update layer panel to reflect changes
            this.updateLayersPanel();

            console.log('💾 Feature salva com sucesso:', featureId);
            this.closeModal();
        }
    }

    deleteFeature() {
        if (!this.selectedFeature) return;

        const featureId = this.selectedFeature._featureId;
        
        if (confirm('Tem certeza que deseja excluir este elemento?')) {
            // Remove from map
            this.drawnItems.removeLayer(this.selectedFeature);
            
            // Remove from features collection
            this.features.delete(featureId);
            
            // Update layer panel
            this.updateLayersPanel();
            
            console.log('🗑️ Feature deletada:', featureId);
            
            this.closeModal();
        }
    }

    closeModal() {
        const modal = document.getElementById('geojson-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.selectedFeature = null;
    }

    openTableView() {
        const modal = document.getElementById('table-modal');
        if (!modal) return;

        this.populateTable();
        modal.style.display = 'flex';
    }

    populateTable() {
        const tbody = document.getElementById('features-table-body');
        if (!tbody) return;

        tbody.innerHTML = '';

        this.features.forEach((feature, id) => {
            const row = document.createElement('tr');
            
            const nameProperty = feature.properties.name || feature.properties.title || feature.properties.no_gleba || '';
            const measurement = this.getFeatureMeasurement(feature);
            
            row.innerHTML = `
                <td>${id.substring(0, 8)}...</td>
                <td>${this.capitalizeFirst(feature.type)}</td>
                <td>${nameProperty}</td>
                <td>${measurement}</td>
                <td>
                    <button class="table-action-btn table-edit-btn" onclick="geojsonInterface.editFeatureFromTable('${id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="table-action-btn table-delete-btn" onclick="geojsonInterface.deleteFeatureFromTable('${id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    editFeatureFromTable(featureId) {
        const featureData = this.features.get(featureId);
        if (featureData) {
            this.selectedFeature = featureData.layer;
            this.closeTableModal();
            this.openModal(featureData.layer);
        }
    }

    deleteFeatureFromTable(featureId) {
        const featureData = this.features.get(featureId);
        if (featureData && confirm('Are you sure you want to delete this feature?')) {
            this.drawnItems.removeLayer(featureData.layer);
            this.features.delete(featureId);
            this.populateTable(); // Refresh table
            this.updateLayersPanel(); // Update layer panel
        }
    }

    resetToPanMode() {
        // Disable all drawing tools
        Object.values(this.drawControls).forEach(control => {
            if (control.disable) control.disable();
        });

        // Update toolbar UI
        document.querySelectorAll('.geojson-btn').forEach(btn => btn.classList.remove('active'));
        const panBtn = document.getElementById('pan-mode');
        if (panBtn) {
            panBtn.classList.add('active');
        }

        // Set current tool to pan
        this.currentTool = 'pan';
        
        console.log('🖱️ Voltou para modo pan');
    }

    closeTableModal() {
        const modal = document.getElementById('table-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    saveAllData() {
        // Export all features as GeoJSON
        const geojson = {
            type: 'FeatureCollection',
            features: Array.from(this.features.values()).map(feature => ({
                type: 'Feature',
                properties: feature.properties,
                geometry: feature.geometry
            }))
        };

        const blob = new Blob([JSON.stringify(geojson, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'features.geojson';
        a.click();
        URL.revokeObjectURL(url);
    }
    
    async clearAllFeatures() {
        if (!confirm('Tem certeza que deseja remover TODAS as features? Esta ação não pode ser desfeita.')) {
            return;
        }
        
        try {
            // Limpar do mapa
            this.drawnItems.clearLayers();
            
            // Limpar do armazenamento local
            this.features.clear();
            
            // Atualizar painel de camadas
            this.updateLayersPanel();
            
            // Fechar modal se estiver aberto
            this.closeModal();
            
            console.log('🗑️ Todas as features foram removidas');
            
            // Opcional: chamar API do backend se houver persistência
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
                    console.log('✅ Features removidas do backend');
                } else {
                    console.warn('⚠️ Erro ao limpar backend, mas features removidas localmente');
                }
            } catch (error) {
                console.warn('⚠️ Não foi possível limpar backend:', error);
            }
            
        } catch (error) {
            console.error('❌ Erro ao limpar features:', error);
        }
    }

    // Utility methods
    generateFeatureId() {
        return 'feature_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    formatArea(area) {
        if (area < 10000) {
            return Math.round(area) + ' m²';
        } else {
            return (area / 10000).toFixed(2) + ' ha';
        }
    }

    formatDistance(distance) {
        if (distance < 1000) {
            return Math.round(distance) + ' m';
        } else {
            return (distance / 1000).toFixed(2) + ' km';
        }
    }

    calculateLength(latlngs) {
        let total = 0;
        for (let i = 0; i < latlngs.length - 1; i++) {
            total += latlngs[i].distanceTo(latlngs[i + 1]);
        }
        return total;
    }

    simplifyCoordinates(coords) {
        if (Array.isArray(coords[0])) {
            return `${coords.length} points`;
        }
        return `[${coords[1].toFixed(4)}, ${coords[0].toFixed(4)}]`;
    }

    getFeatureMeasurement(feature) {
        if (feature.type === 'polygon' || feature.type === 'rectangle') {
            const area = L.GeometryUtil.geodesicArea(feature.layer.getLatLngs()[0]);
            return this.formatArea(area);
        } else if (feature.type === 'polyline') {
            const length = this.calculateLength(feature.layer.getLatLngs());
            return this.formatDistance(length);
        }
        return '-';
    }

    capitalizeFirst(str) {
        if (!str || typeof str !== 'string') return 'Feature';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    applySimplestyles(layer, properties) {
        const style = {};
        
        if (properties.fill) style.fillColor = properties.fill;
        if (properties['fill-opacity']) style.fillOpacity = parseFloat(properties['fill-opacity']);
        if (properties.stroke) style.color = properties.stroke;
        if (properties['stroke-opacity']) style.opacity = parseFloat(properties['stroke-opacity']);
        if (properties['stroke-width']) style.weight = parseInt(properties['stroke-width']);

        if (layer.setStyle) {
            layer.setStyle(style);
        }
    }
}

// Initialize the interface when WebGIS is ready
document.addEventListener('webgisReady', (event) => {
    console.log('🎯 Inicializando interface geojson.io...');
    if (!window.geojsonInterface) {
        window.geojsonInterface = new GeojsonStyleInterface();
        // Disponibilizar clearAllFeatures globalmente para o botão
        window.GeoJsonTools = window.GeoJsonTools || {};
        window.GeoJsonTools.clearAllFeatures = () => window.geojsonInterface.clearAllFeatures();
    }
});

// Fallback: initialize when mapReady is triggered
document.addEventListener('mapReady', (event) => {
    setTimeout(() => {
        if (!window.geojsonInterface) {
            console.log('🎯 Inicializando interface geojson.io (mapReady)...');
            window.geojsonInterface = new GeojsonStyleInterface();
        }
    }, 200);
});

// Ultimate fallback: initialize when DOM is ready if map already exists
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (!window.geojsonInterface && window.webgisReady) {
            console.log('🎯 Inicializando interface geojson.io (DOM ready)...');
            window.geojsonInterface = new GeojsonStyleInterface();
        }
    }, 1000);
});

// Hook para integração com sistema de importação existente
window.addImportedFeatureToGeojsonInterface = function(layer, properties) {
    if (window.geojsonInterface && window.geojsonInterface.addImportedFeature) {
        return window.geojsonInterface.addImportedFeature(layer, properties);
    } else {
        console.warn('GeojsonInterface não inicializada ainda');
        return null;
    }
};