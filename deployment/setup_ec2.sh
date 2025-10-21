#!/bin/bash
set -e

echo "=========================================="
echo "EC2 Setup Script for Task Management App"
echo "=========================================="

echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo "Installing Docker..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

echo "Adding current user to docker group..."
sudo usermod -aG docker $USER

echo "Starting and enabling Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Installing Git..."
sudo apt install -y git

echo "Creating application directory..."
sudo mkdir -p /opt/taskapp
sudo chown -R $USER:$USER /opt/taskapp

echo "Installing Nginx (optional)..."
sudo apt install -y nginx

echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Log out and log back in for docker group to take effect"
echo "2. Create .env file in /opt/taskapp/"
echo "3. Run deploy.sh to deploy the application"
echo ""
echo "Verify Docker installation:"
echo "  docker --version"
echo "  docker-compose --version"
