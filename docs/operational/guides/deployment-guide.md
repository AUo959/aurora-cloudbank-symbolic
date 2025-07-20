# Deployment Guide

This guide provides comprehensive instructions for deploying Aurora CloudBank in various environments.

## 🚀 Quick Start Deployment

### Prerequisites
- Node.js 20 or higher
- Python 3.12 or higher  
- Git
- Docker (optional, for containerized deployment)

### Local Development Deployment

```bash
# Clone the repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Install dependencies
make install
# or manually:
pip install -r requirements.txt
npm install

# Start the development server
make run
# or manually:
./launch-demo.sh
```

The application will be available at:
- **API Server:** http://localhost:8000
- **Web Interface:** http://localhost:8000 (served by FastAPI)

### Production Deployment Options

#### Option 1: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Services will be available at:
# - Main application: http://localhost:8000
# - Command Node: http://localhost:3001
```

#### Option 2: GitHub Pages (Demo)

The live demo is automatically deployed to GitHub Pages:
- **URL:** https://auo959.github.io/aurora-cloudbank-symbolic
- **Update Process:** Push to `main` branch triggers automatic deployment
- **Static Assets:** Served from `/static` directory

#### Option 3: Cloud Deployment

For cloud platforms (AWS, GCP, Azure):

```bash
# Prepare environment
export ENVIRONMENT=production
export PORT=8000

# Install production dependencies
pip install -r requirements.txt --no-dev

# Start production server
uvicorn aurora_api_server:app --host 0.0.0.0 --port $PORT
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Configuration
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0

# Security
SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_HOURS=24

# External APIs (optional)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# Database (if using persistent storage)
DATABASE_URL=sqlite:///aurora.db
```

### Feature Flags

Control features through environment variables:

```env
# Enable/disable features
ENABLE_QUANTUM_PROCESSING=true
ENABLE_VSA_OPERATIONS=true
ENABLE_CASK_SIMULATION=true
ENABLE_SONNET4_INTEGRATION=true
```

## 🔧 Service Configuration

### FastAPI Backend

Main application server configuration:

```python
# Key configuration in aurora_api_server.py
app = FastAPI(
    title="Aurora CloudBank API",
    description="Quantum VSA Symbolic System",
    version="1.0.0"
)
```

### Node.js Command Node

Auxiliary service for command processing:

```javascript
// Service configuration in services/command_node/
const PORT = process.env.NODE_PORT || 3001;
const app = express();
```

### ORION Station Integration

Optional bridge service for multi-instance communication:

```bash
# Start bridge server
python -m modules.instance_bridge.bridge_server

# Connect clients
python -m modules.instance_bridge.bridge_client ws://localhost:8090 main example-id
```

## 📊 Health Checks

### Application Health Endpoints

- **Health Check:** GET `/health`
- **API Status:** GET `/status`
- **Metrics:** GET `/metrics` (if enabled)

### System Monitoring

```bash
# Check system status
python scripts/dev-status.py

# Run comprehensive health check
bash .aurora/system/on_startup.sh

# Monitor resource usage
python performance_benchmark.py
```

## 🔄 Updates and Maintenance

### Automated Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade
npm update

# Run tests after updates
npm test
python -m pytest tests/
```

### Database Migrations (if applicable)

```bash
# Apply database changes
python scripts/database_migration.py --apply

# Backup before major changes
python scripts/orion_backup_sync.py --backup
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### Module Import Errors
```bash
# Ensure Python path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Docker Issues
```bash
# Clean rebuild containers
docker-compose down --volumes
docker-compose up --build
```

### Performance Optimization

#### Memory Issues
```bash
# Monitor and limit language servers
./monitor_and_kill_pylance.sh
./kill_heavy_language_servers.sh
```

#### CPU Optimization
```bash
# Run performance optimization
./optimize_performance.sh
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer with multiple FastAPI instances
- Implement session stickiness if using in-memory state
- Consider Redis for shared state management

### Vertical Scaling
- Monitor memory usage with quantum processing workloads
- CPU requirements scale with VSA vector operations
- Storage needs minimal for stateless deployment

## 🔐 Security in Deployment

### Production Security Checklist
- [ ] Change default secrets and keys
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure rate limiting for public APIs
- [ ] Set up proper CORS policies
- [ ] Enable security headers (Helmet.js configured)
- [ ] Regular security updates for dependencies

### Network Security
```bash
# Firewall configuration (example)
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
```

## 📞 Support and Monitoring

### Logging
- **Application logs:** Available in `/logs` directory
- **Access logs:** FastAPI access logging enabled
- **Error logs:** Comprehensive error tracking and reporting

### Monitoring Integration
```bash
# Custom monitoring setup
python scripts/monitoring_setup.py

# Health check automation
python scripts/health_check_scheduler.py
```

For additional support, see the main documentation or create an issue in the repository.