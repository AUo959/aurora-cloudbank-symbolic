# Component Synergy Dashboard - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start the API Server

```bash
cd /home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic
python api/aurora_api.py
```

### Step 2: Open the Dashboard

Navigate to: **http://localhost:8000/static/synergy-dashboard.html**

### Step 3: Explore!

- View 8 R-2 agent components
- Monitor real-time health metrics
- Explore component interactions
- Track synergy scores

## 📊 What You'll See

### Dashboard Metrics (Top)
- **Total Components**: 8 registered components
- **Active Components**: Number of healthy components
- **Total Interactions**: Component communication paths
- **Average Synergy Score**: Overall integration quality
- **System Health**: Aggregate health percentage

### Component Status Cards
Each component shows:
- ✅ Status badge (active/degraded/offline)
- 📊 Health bar (0-100%)
- 💻 CPU usage percentage
- 🧠 Memory usage in MB
- 🔍 Click for detailed view

### Interactive Topology
- Circular graph showing all components
- Color-coded by health (green=good, yellow=warning, red=critical)
- Lines show interactions between components

### Synergy Scores
- Component pair analysis
- Integration level (full/partial/none)
- Optimization opportunities
- Trend indicators (↗ increasing, → stable, ↘ decreasing)

## 🎯 Quick Actions

### Filter Components
- **All Components**: Show everything
- **Active Only**: Hide degraded/offline
- **Degraded**: Show only struggling components
- **Offline**: Show only offline components

### Search Components
Type in the search box to filter by:
- Component name
- Component ID

### View Details
Click any component card or "View Details" button to see:
- Full status information
- Resource usage details
- All interactions involving the component
- Historical data (future feature)

## 🔌 API Endpoints

All endpoints available at `http://localhost:8000/api/synergy/`

### Get System Metrics
```bash
curl http://localhost:8000/api/synergy/metrics
```

### Get All Components
```bash
curl http://localhost:8000/api/synergy/components
```

### Get Active Components Only
```bash
curl http://localhost:8000/api/synergy/components?status_filter=active
```

### Get Component Topology
```bash
curl http://localhost:8000/api/synergy/topology
```

### Get Component Interactions
```bash
curl http://localhost:8000/api/synergy/interactions
```

### Get Synergy Scores
```bash
curl http://localhost:8000/api/synergy/synergy-scores
```

### Health Check
```bash
curl http://localhost:8000/api/synergy/health
```

## 📱 Features

- ✅ Real-time updates (every 5 seconds)
- ✅ WebSocket push notifications
- ✅ Responsive design (works on mobile!)
- ✅ Search and filter
- ✅ Interactive visualizations
- ✅ Detailed component views
- ✅ DLP tracking for all operations

## 🎨 Dashboard Components

### 8 Monitored Components

1. **AuMemManager** - Quantum memory (56K capacity)
2. **Data Guardian** - PII detection and redaction
3. **Insight Ledger** - Cryptographic audit trail
4. **Quantum Simulator** - Quantum scenario simulation
5. **DLP Tracker** - Data lineage tracking
6. **ChatGPT Agent Mode** - Agent tool registry
7. **Symbolic Engine** - Chain notation processing
8. **Thread Transfer Bridge** - Cross-thread continuity

### 6 Known Synergies

- AuMemManager ↔ Data Guardian (85%)
- DLP Tracker ↔ Insight Ledger (90%)
- Quantum Simulator ↔ DLP Tracker (80%)
- AuMemManager ↔ Insight Ledger (75%)
- ChatGPT Agent ↔ AuMemManager (70%)
- ChatGPT Agent ↔ Quantum Simulator (65%)

## 🛠️ Troubleshooting

### Dashboard Won't Load
- Check API server is running
- Verify URL is correct
- Check browser console for errors

### WebSocket Not Connecting
- Ensure token parameter is set
- Check firewall/proxy settings
- Try refreshing the page

### Components Not Showing
- Verify API responds: `curl http://localhost:8000/api/synergy/components`
- Check server logs for errors
- Ensure database/registry is accessible

## 📚 More Information

- Full Documentation: `docs/SYNERGY_DASHBOARD_UI.md`
- Implementation Details: `SYNERGY_DASHBOARD_IMPLEMENTATION.md`
- API Tests: `tests/test_synergy_dashboard.py`

## 🔒 Security

- WebSocket requires authentication token
- Content Security Policy enforced
- All operations tracked with DLP
- Input validation on all endpoints

## 💡 Tips

1. **Use filters** to focus on specific component states
2. **Search** to quickly find components
3. **Click components** for detailed information
4. **Watch the topology** to understand interactions
5. **Monitor synergy scores** for integration opportunities

---

**Need Help?** Check the full documentation in `docs/SYNERGY_DASHBOARD_UI.md`
