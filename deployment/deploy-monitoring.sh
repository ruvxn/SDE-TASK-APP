#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Monitoring Stack to EC2"
echo "Level 2: Prometheus + Grafana"
echo "=========================================="
echo ""

APP_DIR="/opt/taskapp"
COMPOSE_FILE="docker-compose.monitoring.yml"

# Check if we're in the right directory
if [ ! -d "$APP_DIR" ]; then
    echo "ERROR: Application directory $APP_DIR not found"
    echo "Please ensure the app is set up in $APP_DIR"
    exit 1
fi

cd $APP_DIR

# Pull latest code
echo "Pulling latest code from GitHub..."
if [ -d ".git" ]; then
    git pull origin main
else
    echo "WARNING: Not a git repository. Please pull code manually."
    echo "Run: git clone <your-repo> $APP_DIR"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "ERROR: $COMPOSE_FILE not found"
    echo "Please ensure you pushed the monitoring configuration to GitHub"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/project_management

# Application Configuration
SECRET_KEY=production-secret-key-change-this-immediately
FLASK_ENV=production

# Grafana Configuration
GF_SECURITY_ADMIN_PASSWORD=admin
EOF
    echo "Created .env file. IMPORTANT: Change SECRET_KEY and GF_SECURITY_ADMIN_PASSWORD!"
fi

# Stop any existing containers
echo ""
echo "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down 2>/dev/null || true

# Build and start monitoring stack
echo ""
echo "Starting monitoring stack..."
echo "This will start: PostgreSQL, Flask App, Prometheus, Grafana"
docker-compose -f $COMPOSE_FILE up -d --build

# Wait for services to start
echo ""
echo "Waiting for services to start (30 seconds)..."
sleep 30

# Check container status
echo ""
echo "Checking container status..."
docker-compose -f $COMPOSE_FILE ps

# Health checks
echo ""
echo "Running health checks..."

# Check Flask app
if curl -f http://localhost:5000 >/dev/null 2>&1; then
    echo "✓ Flask app is responding"
else
    echo "✗ Flask app health check failed"
fi

# Check metrics endpoint
if curl -f http://localhost:5000/metrics >/dev/null 2>&1; then
    echo "✓ Metrics endpoint is responding"
else
    echo "✗ Metrics endpoint health check failed"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo "✓ Prometheus is healthy"
else
    echo "✗ Prometheus health check failed"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
    echo "✓ Grafana is healthy"
else
    echo "✗ Grafana health check failed"
fi

# Get EC2 public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "UNKNOWN")

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Services running:"
docker-compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Access URLs (after opening security group ports):"
echo "  Flask App:   http://$PUBLIC_IP:5000"
echo "  Prometheus:  http://$PUBLIC_IP:9090"
echo "  Grafana:     http://$PUBLIC_IP:3000"
echo ""
echo "Grafana Login:"
echo "  Username: admin"
echo "  Password: admin (change immediately!)"
echo ""
echo "Next steps:"
echo "1. Open AWS Security Group and add inbound rules:"
echo "   - Port 3000 (Grafana) - Source: Your IP"
echo "   - Port 9090 (Prometheus) - Source: Your IP"
echo "   - Port 5000 (Flask App) - Source: Your IP or 0.0.0.0/0"
echo ""
echo "2. Access Grafana: http://$PUBLIC_IP:3000"
echo "3. Import dashboard or create custom visualizations"
echo ""
echo "View logs:"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "Stop stack:"
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
