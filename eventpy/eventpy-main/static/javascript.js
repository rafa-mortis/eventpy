/**
 * ============================================
 * REECLAGEM REEE LISBOA - Optimized JavaScript
 * ============================================
 */

// ===== GLOBAL VARIABLES =====
let map = null;
let markers = [];
let pointsData = [];
let userLocation = null;

// ===== CONFIGURATION =====
const CONFIG = {
    MAP: {
        DEFAULT_CENTER: [38.7169, -9.1333], // Lisbon
        DEFAULT_ZOOM: 12,
        MIN_ZOOM: 8,
        MAX_ZOOM: 18
    },
    API: {
        POINTS_ENDPOINT: '/api/pontos_recolha',
        TIMEOUT: 10000
    },
    ICONS: {
        'centro_rececao': '🏢',
        'ecocentro': '♻️',
        'entrajuda': '🤝',
        'ponto_eletrao': '⚡',
        'recolha_municipal': '🏘️'
    },
    COLORS: {
        'centro_rececao': '#1976d2',
        'ecocentro': '#388e3c',
        'entrajuda': '#f57c00',
        'ponto_eletrao': '#7b1fa2',
        'recolha_municipal': '#c62828'
    }
};

// ===== UTILITY FUNCTIONS =====
function debounce(func, wait) {
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

function formatDistance(distance) {
    return distance < 1000 ? `${Math.round(distance)}m` : `${(distance / 1000).toFixed(1)}km`;
}

function showLoading(element) {
    if (element) element.classList.add('loading');
}

function hideLoading(element) {
    if (element) element.classList.remove('loading');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.notifications-container') || createNotificationContainer();
    container.appendChild(notification);
    
    setTimeout(() => notification.remove(), 5000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notifications-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
    document.body.appendChild(container);
    return container;
}

// ===== MAP FUNCTIONS =====
async function initializeMap() {
    try {
        if (typeof L === 'undefined') throw new Error('Leaflet library not loaded');

        map = L.map('map').setView(CONFIG.MAP.DEFAULT_CENTER, CONFIG.MAP.DEFAULT_ZOOM);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: ' OpenStreetMap contributors',
            maxZoom: CONFIG.MAP.MAX_ZOOM,
            minZoom: CONFIG.MAP.MIN_ZOOM
        }).addTo(map);

        await getUserLocation();
        await loadPoints();
        setupMapEvents();
        
        showNotification('Mapa carregado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Error initializing map:', error);
        showNotification('Erro ao carregar o mapa. Por favor, tente novamente.', 'danger');
    }
}

async function getUserLocation() {
    return new Promise((resolve) => {
        if (!navigator.geolocation) {
            console.log('Geolocation not supported');
            resolve(null);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                if (map) {
                    L.marker([userLocation.lat, userLocation.lng], {
                        icon: L.divIcon({
                            className: 'user-location-marker',
                            html: '',
                            iconSize: [30, 30]
                        })
                    }).addTo(map).bindPopup('A sua localização').openPopup();
                    
                    map.setView([userLocation.lat, userLocation.lng], 13);
                }
                
                resolve(userLocation);
            },
            (error) => {
                console.log('Error getting location:', error);
                resolve(null);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
        );
    });
}

async function loadPoints() {
    try {
        showLoading(document.querySelector('#map'));
        
        const response = await fetch(CONFIG.API.POINTS_ENDPOINT, { timeout: CONFIG.API.TIMEOUT });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        pointsData = await response.json();
        console.log(`Loaded ${pointsData.length} points from API`);
        
        // Debug: Check point types distribution
        const typeCounts = {};
        pointsData.forEach(point => {
            typeCounts[point.tipo_ponto] = (typeCounts[point.tipo_ponto] || 0) + 1;
        });
        console.log('Point types distribution:', typeCounts);
        
        // Check for invalid coordinates
        const invalidPoints = pointsData.filter(p => !p.latitude || !p.longitude || p.latitude === 0 || p.longitude === 0);
        if (invalidPoints.length > 0) {
            console.warn(`Found ${invalidPoints.length} points with invalid coordinates:`, invalidPoints);
        }
        
        clearMarkers();
        pointsData.forEach(point => addMarker(point));
        updatePointsCount(pointsData.length);
        
        console.log(`Successfully added ${markers.length} markers to map`);
        
    } catch (error) {
        console.error('Error loading points:', error);
        showNotification('Erro ao carregar os pontos de recolha.', 'danger');
    } finally {
        hideLoading(document.querySelector('#map'));
    }
}

function addMarker(point) {
    if (!map || !point.latitude || !point.longitude) return;
    
    const icon = L.divIcon({
        className: `custom-marker marker-${point.tipo_ponto}`,
        html: `<div style="background: ${CONFIG.COLORS[point.tipo_ponto]}; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${CONFIG.ICONS[point.tipo_ponto] || ''}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -15]
    });
    
    const marker = L.marker([point.latitude, point.longitude], { icon })
        .addTo(map)
        .bindPopup(createPopupContent(point));
    
    // Add distance if user location is available
    if (userLocation) {
        const distance = calculateDistance(userLocation.lat, userLocation.lng, point.latitude, point.longitude);
        marker.setPopupContent(marker.getPopup().getContent() + 
            `<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <strong>Distância:</strong> ${formatDistance(distance)}
            </div>`);
    }
    
    markers.push(marker);
}

function createPopupContent(point) {
    return `
        <div style="min-width: 200px;">
            <h6 style="margin: 0 0 10px 0; color: #333;">${point.nome}</h6>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>Morada:</strong> ${point.morada}<br>
                <strong>Freguesia:</strong> ${point.freguesia}<br>
                ${point.bairro ? `<strong>Bairro:</strong> ${point.bairro}<br>` : ''}
                <strong>Tipo:</strong> <span class="point-type-badge type-${point.tipo_ponto}">${point.tipo_ponto.replace('_', ' ')}</span><br>
                ${point.horario_abertura && point.horario_fecho ? `<strong>Horário:</strong> ${point.horario_abertura} - ${point.horario_fecho}<br>` : ''}
                ${point.dias_funcionamento ? `<strong>Dias:</strong> ${point.dias_funcionamento}<br>` : ''}
                ${point.telefone ? `<strong>Telefone:</strong> <a href="tel:${point.telefone}">${point.telefone}</a><br>` : ''}
                ${point.email ? `<strong>Email:</strong> <a href="mailto:${point.email}">${point.email}</a>` : ''}
            </p>
            ${point.website ? `<a href="${point.website}" target="_blank" class="btn btn-sm btn-primary">Visitar Website</a>` : ''}
        </div>
    `;
}

function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c * 1000; // Convert to meters
}

function setupMapEvents() {
    if (!map) return;
    
    map.on('click', function(e) {
        console.log('Map clicked at:', e.latlng);
    });
    
    map.on('zoomend', function() {
        console.log('Map zoomed to:', map.getZoom());
    });
}

// ===== SEARCH FUNCTIONS =====
function initializeSearch() {
    const searchForm = document.querySelector('#search-form');
    const searchInput = document.querySelector('#search-input');
    const filterSelects = document.querySelectorAll('.filter-select');
    
    if (searchForm) searchForm.addEventListener('submit', handleSearch);
    if (searchInput) searchInput.addEventListener('input', debounce(handleSearchInput, 300));
    filterSelects.forEach(select => select.addEventListener('change', handleSearch));
}

function handleSearch(e) {
    e.preventDefault();
    performSearch();
}

function handleSearchInput(e) {
    const query = e.target.value.trim();
    if (query.length >= 2 || query.length === 0) performSearch();
}

function handleFilterChange() {
    performSearch();
}

function performSearch() {
    const formData = new FormData(document.querySelector('#search-form') || document.querySelector('form'));
    const filters = {
        query: formData.get('query') || '',
        freguesia: formData.get('freguesia') || '',
        bairro: formData.get('bairro') || '',
        tipo_ponto: formData.get('tipo_ponto') || ''
    };
    
    const filteredPoints = pointsData.filter(point => {
        // Text search
        if (filters.query) {
            const searchText = filters.query.toLowerCase();
            const searchableText = [point.nome, point.morada, point.freguesia, point.bairro, point.tipo_ponto].join(' ').toLowerCase();
            if (!searchableText.includes(searchText)) return false;
        }
        
        // Filter checks
        if (filters.freguesia && point.freguesia !== filters.freguesia) return false;
        if (filters.bairro && point.bairro !== filters.bairro) return false;
        if (filters.tipo_ponto && point.tipo_ponto !== filters.tipo_ponto) return false;
        
        return true;
    });
    
    updateMapWithFilteredPoints(filteredPoints);
    updateResultsList(filteredPoints);
    updatePointsCount(filteredPoints.length);
}

function updateMapWithFilteredPoints(filteredPoints) {
    clearMarkers();
    filteredPoints.forEach(point => addMarker(point));
    
    if (filteredPoints.length > 0 && markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

function updateResultsList(points) {
    const resultsContainer = document.querySelector('#results-list');
    if (!resultsContainer) return;
    
    if (points.length === 0) {
        resultsContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    <h5>Nenhum resultado encontrado</h5>
                    <p>Tente ajustar os filtros de pesquisa.</p>
                </div>
            </div>
        `;
        return;
    }
    
    resultsContainer.innerHTML = points.map(point => createResultCard(point)).join('');
}

function createResultCard(point) {
    const distance = userLocation ? 
        calculateDistance(userLocation.lat, userLocation.lng, point.latitude, point.longitude) : null;
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="point-card">
                <div class="point-type-badge type-${point.tipo_ponto}">
                    ${point.tipo_ponto.replace('_', ' ')}
                </div>
                <h5>${point.nome}</h5>
                <p class="text-muted">
                     ${point.morada}<br>
                    ${point.freguesia}${point.bairro ? `, ${point.bairro}` : ''}
                </p>
                ${distance ? `<p class="text-primary"><strong>Distância:</strong> ${formatDistance(distance)}</p>` : ''}
                <div class="mt-3">
                    <button class="btn btn-sm btn-primary" onclick="focusOnPoint(${point.latitude}, ${point.longitude})">
                         Ver no Mapa
                    </button>
                    ${point.telefone ? 
                        `<a href="tel:${point.telefone}" class="btn btn-sm btn-outline-primary ms-2">
                            Ligar
                        </a>` : ''}
                </div>
            </div>
        </div>
    `;
}

function focusOnPoint(lat, lng) {
    if (map) {
        map.setView([lat, lng], 16);
        
        markers.forEach(marker => {
            const markerLatLng = marker.getLatLng();
            if (Math.abs(markerLatLng.lat - lat) < 0.0001 && Math.abs(markerLatLng.lng - lng) < 0.0001) {
                marker.openPopup();
            }
        });
    }
}

function updatePointsCount(count) {
    // Update elements with class .points-count
    document.querySelectorAll('.points-count').forEach(element => {
        element.textContent = count;
    });
    
    // Update element with ID #total-pontos (for index.html)
    const totalPontosElement = document.getElementById('total-pontos');
    if (totalPontosElement) {
        totalPontosElement.textContent = count;
    }
}

// ===== FORM FUNCTIONS =====
function initializeForms() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

function handleFormSubmit(e) {
    const form = e.target;
    
    if (!validateForm(form)) {
        e.preventDefault();
        showNotification('Por favor, corrija os erros no formulário.', 'warning');
        return;
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner"></span> A processar...';
    }
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) isValid = false;
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório.';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Por favor, insira um email válido.';
        }
    }
    
    // Phone validation
    if (field.name === 'telefone' && value) {
        const phoneRegex = /^[+]?[\d\s\-\(\)]+$/;
        if (!phoneRegex.test(value) || value.length < 9) {
            isValid = false;
            errorMessage = 'Por favor, insira um número de telefone válido.';
        }
    }
    
    if (isValid) {
        clearFieldError(field);
    } else {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) errorElement.remove();
}

// ===== UTILITY FUNCTIONS =====
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Texto copiado para a área de transferência!', 'success');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        showNotification('Erro ao copiar texto.', 'danger');
    }
}

async function sharePage(title, text, url) {
    if (navigator.share) {
        try {
            await navigator.share({ title, text, url });
        } catch (err) {
            console.log('Share cancelled or failed:', err);
        }
    } else {
        copyToClipboard(url);
    }
}

function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-PT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize map if map container exists
    if (document.getElementById('map')) initializeMap();
    
    // Initialize search if search form exists
    if (document.querySelector('#search-form') || document.querySelector('.filter-select')) initializeSearch();
    
    // Initialize forms if any have validation
    if (document.querySelector('form[data-validate]')) initializeForms();
    
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href').substring(1);
            if (targetId) {
                e.preventDefault();
                scrollToElement(targetId);
            }
        });
    });
    
    console.log('REEE Reciclagem JavaScript initialized successfully');
});

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    
    if (window.REEE && window.REEE._errorNotificationsDisabled) return;
    
    const shouldShowError = e.error && e.error.message && 
        !e.error.message.includes('Script error') &&
        !e.error.message.includes('NetworkError') &&
        !e.error.message.includes('Failed to fetch') &&
        !e.error.message.includes('Load failed') &&
        !e.error.message.includes('leaflet') &&
        !e.error.message.includes('OpenStreetMap') &&
        e.filename && e.filename.includes('javascript.js');
    
    if (shouldShowError) {
        showNotification('Ocorreu um erro inesperado. Por favor, recarregue a página.', 'danger');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    
    if (window.REEE && window.REEE._errorNotificationsDisabled) return;
    
    const shouldShowError = e.reason && e.reason.message && 
        !e.reason.message.includes('network') &&
        !e.reason.message.includes('fetch') &&
        !e.reason.message.includes('timeout') &&
        !e.reason.message.includes('AbortError');
    
    if (shouldShowError) {
        showNotification('Ocorreu um erro ao processar a sua solicitação.', 'danger');
    }
});

// ===== EXPORT FUNCTIONS =====
window.REEE = {
    copyToClipboard,
    sharePage,
    scrollToElement,
    focusOnPoint,
    showNotification,
    formatDate,
    loadPoints,
    performSearch,
    debugPoints: () => {
        console.log('=== DEBUG INFO ===');
        console.log(`Total points loaded: ${pointsData.length}`);
        console.log(`Total markers on map: ${markers.length}`);
        const typeCounts = {};
        pointsData.forEach(point => {
            typeCounts[point.tipo_ponto] = (typeCounts[point.tipo_ponto] || 0) + 1;
        });
        console.table(typeCounts);
        console.log('User location:', userLocation);
        console.log('Map bounds:', map ? map.getBounds() : 'Map not initialized');
        return { pointsData, markers, typeCounts, userLocation };
    },
    refreshPoints: () => {
        console.log('Manually refreshing points...');
        loadPoints();
    },
    disableErrorNotifications: () => {
        console.log('Error notifications disabled. Reload page to re-enable.');
        window.REEE._errorNotificationsDisabled = true;
    },
    enableErrorNotifications: () => {
        console.log('Error notifications enabled.');
        window.REEE._errorNotificationsDisabled = false;
    }
};