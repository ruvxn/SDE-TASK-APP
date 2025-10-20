#!/bin/bash

###############################################################################
# Initial setup script for AWS EC2 instance
# Run this once on a new EC2 instance to prepare it for deployments
###############################################################################

set -e  # Exit on error

echo "========================================="
echo "Setting up EC2 instance for TaskApp"
echo "========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed"
fi

# Install Nginx (reverse proxy)
echo "Installing Nginx..."
sudo apt-get install -y nginx

# Configure Nginx
echo "Configuring Nginx as reverse proxy..."
sudo tee /etc/nginx/sites-available/taskapp > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000/;
        access_log off;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/taskapp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/taskapp
sudo chown -R $USER:$USER /opt/taskapp

# Create .env file template
echo "Creating environment file template..."
cat > /opt/taskapp/.env.example <<'EOF'
# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/dbname

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production

# Optional: Monitoring
PROMETHEUS_ENABLED=true
EOF

echo ""
echo "========================================="
echo "EC2 Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create /opt/taskapp/.env with your configuration"
echo "2. Set up PostgreSQL database (RDS or local)"
echo "3. Configure DNS to point to this server"
echo "4. (Optional) Set up SSL certificate with Let's Encrypt"
echo "5. Configure Jenkins to deploy to this server"
echo ""
echo "Useful commands:"
echo "  - View app logs: docker logs taskapp_production"
echo "  - Restart app: docker restart taskapp_production"
echo "  - Check Nginx: sudo systemctl status nginx"
echo "  - View Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo ""
echo "========================================="
