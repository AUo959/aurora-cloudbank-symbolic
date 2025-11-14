/**
 * Aurora Component Synergy Dashboard
 * 
 * Real-time monitoring of R-2 agent component interactions and health
 * DLP: synergy_dashboard_frontend
 */

class SynergyDashboard {
    constructor() {
        this.apiBase = '/api/synergy';
        this.updateInterval = 5000; // 5 seconds
        this.components = [];
        this.topology = null;
        this.interactions = [];
        this.synergyScores = [];
        this.metrics = null;
        this.ws = null;
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Synergy Dashboard...');
        this.setupWebSocket();
        await this.loadInitialData();
        this.startAutoRefresh();
        this.setupEventListeners();
    }
    
    setupWebSocket() {
        // WebSocket for real-time updates
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/agent/stream?token=demo`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket closed, reconnecting...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to setup WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        // Handle real-time updates from WebSocket
        if (data.type === 'component_update') {
            this.updateComponent(data.component);
        } else if (data.type === 'metric_update') {
            this.updateMetrics(data.metrics);
        }
    }
    
    async loadInitialData() {
        try {
            // Load all initial data in parallel
            const [components, topology, interactions, scores, metrics] = await Promise.all([
                this.fetchComponents(),
                this.fetchTopology(),
                this.fetchInteractions(),
                this.fetchSynergyScores(),
                this.fetchMetrics()
            ]);
            
            this.components = components;
            this.topology = topology;
            this.interactions = interactions;
            this.synergyScores = scores;
            this.metrics = metrics;
            
            this.render();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async fetchComponents(statusFilter = null) {
        const url = statusFilter 
            ? `${this.apiBase}/components?status_filter=${statusFilter}`
            : `${this.apiBase}/components`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch components');
        return await response.json();
    }
    
    async fetchTopology() {
        const response = await fetch(`${this.apiBase}/topology`);
        if (!response.ok) throw new Error('Failed to fetch topology');
        return await response.json();
    }
    
    async fetchInteractions(componentId = null) {
        const url = componentId
            ? `${this.apiBase}/interactions?component_id=${componentId}`
            : `${this.apiBase}/interactions`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch interactions');
        return await response.json();
    }
    
    async fetchSynergyScores() {
        const response = await fetch(`${this.apiBase}/synergy-scores`);
        if (!response.ok) throw new Error('Failed to fetch synergy scores');
        return await response.json();
    }
    
    async fetchMetrics() {
        const response = await fetch(`${this.apiBase}/metrics`);
        if (!response.ok) throw new Error('Failed to fetch metrics');
        return await response.json();
    }
    
    startAutoRefresh() {
        setInterval(async () => {
            try {
                const [components, metrics] = await Promise.all([
                    this.fetchComponents(),
                    this.fetchMetrics()
                ]);
                this.components = components;
                this.metrics = metrics;
                this.updateDashboard();
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, this.updateInterval);
    }
    
    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.applyFilter(e.target.dataset.filter);
            });
        });
        
        // Search input
        const searchInput = document.getElementById('component-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchComponents(e.target.value);
            });
        }
        
        // Component detail buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-component-id]')) {
                this.showComponentDetails(e.target.dataset.componentId);
            }
        });
    }
    
    render() {
        this.renderMetrics();
        this.renderComponents();
        this.renderTopology();
        this.renderInteractions();
        this.renderSynergyScores();
    }
    
    renderMetrics() {
        if (!this.metrics) return;
        
        const metricsContainer = document.getElementById('metrics-summary');
        if (!metricsContainer) return;
        
        const healthColor = this.getHealthColor(this.metrics.system_health);
        
        metricsContainer.innerHTML = `
            <div class="metric-card">
                <h3>Total Components</h3>
                <div class="metric-value">${this.metrics.total_components}</div>
            </div>
            <div class="metric-card">
                <h3>Active Components</h3>
                <div class="metric-value" style="color: #4CAF50;">
                    ${this.metrics.active_components}
                </div>
            </div>
            <div class="metric-card">
                <h3>Total Interactions</h3>
                <div class="metric-value">${this.metrics.total_interactions}</div>
            </div>
            <div class="metric-card">
                <h3>Avg Synergy Score</h3>
                <div class="metric-value">${this.metrics.average_synergy_score.toFixed(1)}%</div>
            </div>
            <div class="metric-card">
                <h3>System Health</h3>
                <div class="metric-value" style="color: ${healthColor};">
                    ${this.metrics.system_health.toFixed(1)}%
                </div>
            </div>
        `;
    }
    
    renderComponents() {
        const container = document.getElementById('components-list');
        if (!container) return;
        
        container.innerHTML = this.components.map(comp => {
            const statusColor = this.getStatusColor(comp.status);
            const healthColor = this.getHealthColor(comp.health_score);
            
            return `
                <div class="component-card" data-component-id="${comp.component_id}">
                    <div class="component-header">
                        <h4>${comp.name}</h4>
                        <span class="status-badge" style="background: ${statusColor};">
                            ${comp.status}
                        </span>
                    </div>
                    <div class="component-body">
                        <div class="health-bar-container">
                            <div class="health-bar" style="width: ${comp.health_score}%; background: ${healthColor};"></div>
                        </div>
                        <div class="component-stats">
                            <span>Health: ${comp.health_score.toFixed(1)}%</span>
                            <span>CPU: ${comp.resource_usage.cpu_percent.toFixed(1)}%</span>
                            <span>Memory: ${comp.resource_usage.memory_mb.toFixed(0)}MB</span>
                        </div>
                    </div>
                    <button class="detail-button" data-component-id="${comp.component_id}">
                        View Details
                    </button>
                </div>
            `;
        }).join('');
    }
    
    renderTopology() {
        const container = document.getElementById('topology-visualization');
        if (!container || !this.topology) return;
        
        // Simple force-directed graph visualization
        const svg = this.createTopologyGraph(this.topology);
        container.innerHTML = '';
        container.appendChild(svg);
    }
    
    createTopologyGraph(topology) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '400');
        svg.setAttribute('viewBox', '0 0 800 400');
        
        // Draw nodes
        const nodeRadius = 30;
        const centerX = 400;
        const centerY = 200;
        const angleStep = (2 * Math.PI) / topology.nodes.length;
        
        topology.nodes.forEach((node, index) => {
            const angle = index * angleStep;
            const x = centerX + 150 * Math.cos(angle);
            const y = centerY + 150 * Math.sin(angle);
            
            // Draw edges first (so nodes appear on top)
            topology.edges.forEach(edge => {
                if (edge.source === node.id) {
                    const targetIndex = topology.nodes.findIndex(n => n.id === edge.target);
                    if (targetIndex >= 0) {
                        const targetAngle = targetIndex * angleStep;
                        const targetX = centerX + 150 * Math.cos(targetAngle);
                        const targetY = centerY + 150 * Math.sin(targetAngle);
                        
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', x);
                        line.setAttribute('y1', y);
                        line.setAttribute('x2', targetX);
                        line.setAttribute('y2', targetY);
                        line.setAttribute('stroke', '#666');
                        line.setAttribute('stroke-width', '2');
                        svg.appendChild(line);
                    }
                }
            });
            
            // Draw node circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', nodeRadius);
            circle.setAttribute('fill', this.getHealthColor(node.health));
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '3');
            circle.setAttribute('class', 'topology-node');
            circle.setAttribute('data-node-id', node.id);
            svg.appendChild(circle);
            
            // Draw node label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', y + nodeRadius + 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#fff');
            text.setAttribute('font-size', '12');
            text.textContent = node.label.substring(0, 10);
            svg.appendChild(text);
        });
        
        return svg;
    }
    
    renderInteractions() {
        const container = document.getElementById('interactions-list');
        if (!container) return;
        
        container.innerHTML = this.interactions.map(inter => `
            <div class="interaction-item">
                <div class="interaction-header">
                    <span class="source">${inter.source_id}</span>
                    <span class="arrow">→</span>
                    <span class="target">${inter.target_id}</span>
                </div>
                <div class="interaction-metrics">
                    <span>Type: ${inter.interaction_type}</span>
                    <span>Freq: ${inter.frequency}/day</span>
                    <span>Latency: ${inter.latency_ms.toFixed(1)}ms</span>
                    <span>Success: ${(inter.success_rate * 100).toFixed(1)}%</span>
                </div>
            </div>
        `).join('');
    }
    
    renderSynergyScores() {
        const container = document.getElementById('synergy-scores-list');
        if (!container) return;
        
        container.innerHTML = this.synergyScores.map(score => {
            const scoreColor = this.getHealthColor(score.score);
            const trendIcon = this.getTrendIcon(score.trend);
            
            return `
                <div class="synergy-card">
                    <div class="synergy-header">
                        <h4>${score.component_pair.join(' ↔ ')}</h4>
                        <span class="trend-badge">${trendIcon} ${score.trend}</span>
                    </div>
                    <div class="synergy-score" style="color: ${scoreColor};">
                        ${score.score.toFixed(1)}%
                    </div>
                    <div class="integration-level">
                        Integration: <span class="badge">${score.integration_level}</span>
                    </div>
                    ${score.opportunities.length > 0 ? `
                        <div class="opportunities">
                            <strong>Opportunities:</strong>
                            <ul>
                                ${score.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
    
    updateDashboard() {
        this.renderMetrics();
        this.renderComponents();
    }
    
    updateComponent(component) {
        const index = this.components.findIndex(c => c.component_id === component.component_id);
        if (index >= 0) {
            this.components[index] = component;
            this.renderComponents();
        }
    }
    
    updateMetrics(metrics) {
        this.metrics = metrics;
        this.renderMetrics();
    }
    
    applyFilter(filter) {
        // Update UI to show active filter
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        
        // Fetch filtered data
        this.fetchComponents(filter === 'all' ? null : filter)
            .then(components => {
                this.components = components;
                this.renderComponents();
            });
    }
    
    searchComponents(query) {
        const filtered = this.components.filter(comp =>
            comp.name.toLowerCase().includes(query.toLowerCase()) ||
            comp.component_id.toLowerCase().includes(query.toLowerCase())
        );
        
        // Render filtered components
        const container = document.getElementById('components-list');
        if (!container) return;
        
        // Use renderComponents logic but with filtered data
        const originalComponents = this.components;
        this.components = filtered;
        this.renderComponents();
        this.components = originalComponents;
    }
    
    showComponentDetails(componentId) {
        // Show modal or expanded view with component details
        const component = this.components.find(c => c.component_id === componentId);
        if (!component) return;
        
        // Filter interactions for this component
        const componentInteractions = this.interactions.filter(
            inter => inter.source_id === componentId || inter.target_id === componentId
        );
        
        // Create modal content
        const modal = document.createElement('div');
        modal.className = 'detail-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${component.name}</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detail-section">
                        <h3>Status</h3>
                        <p>Status: <span class="badge">${component.status}</span></p>
                        <p>Health: ${component.health_score.toFixed(1)}%</p>
                        <p>Uptime: ${Math.floor(component.uptime_seconds / 3600)}h</p>
                    </div>
                    <div class="detail-section">
                        <h3>Resource Usage</h3>
                        <p>CPU: ${component.resource_usage.cpu_percent.toFixed(1)}%</p>
                        <p>Memory: ${component.resource_usage.memory_mb.toFixed(0)}MB</p>
                    </div>
                    <div class="detail-section">
                        <h3>Interactions (${componentInteractions.length})</h3>
                        ${componentInteractions.map(inter => `
                            <div class="interaction-detail">
                                <p>${inter.source_id} → ${inter.target_id}</p>
                                <p>Type: ${inter.interaction_type}</p>
                                <p>Success Rate: ${(inter.success_rate * 100).toFixed(1)}%</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal on click
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    getStatusColor(status) {
        const colors = {
            'active': '#4CAF50',
            'degraded': '#FFC107',
            'offline': '#F44336'
        };
        return colors[status] || '#999';
    }
    
    getHealthColor(health) {
        if (health >= 80) return '#4CAF50';
        if (health >= 60) return '#FFC107';
        if (health >= 40) return '#FF9800';
        return '#F44336';
    }
    
    getTrendIcon(trend) {
        const icons = {
            'increasing': '↗',
            'stable': '→',
            'decreasing': '↘'
        };
        return icons[trend] || '→';
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.synergyDashboard = new SynergyDashboard();
    });
} else {
    window.synergyDashboard = new SynergyDashboard();
}
