#!/bin/bash

# MLOps Platform EC2 Setup Script
# Installs all dependencies: AWS CLI, Git, Docker, Python, Node.js, etc.

set -euo pipefail

echo "=========================================="
echo "MLOps Platform EC2 Setup"
echo "=========================================="

# Update system
echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic tools
echo "Step 2: Installing basic tools..."
sudo apt install -y \
  curl \
  wget \
  unzip \
  zip \
  jq \
  vim \
  git \
  build-essential \
  libssl-dev \
  libffi-dev \
  software-properties-common

# Install AWS CLI v2
echo "Step 3: Installing AWS CLI v2..."
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
cd -
aws --version

# Install Python 3.11
echo "Step 4: Installing Python 3.11..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip || {
  echo "Python 3.11 not available, using python3 instead"
  sudo apt install -y python3 python3-venv python3-dev python3-pip
}
python3 --version

# Install Node.js 20 LTS
echo "Step 5: Installing Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - || true
sudo apt install -y nodejs || {
  echo "NodeSource failed, trying alternative method..."
  curl -fsSL https://fnm.io/install | bash || true
  export PATH="$HOME/.local/share/fnm:$PATH"
  eval "$(fnm env)"
  fnm install 20 || true
}
node --version
npm --version

# Install Docker
echo "Step 6: Installing Docker..."
sudo apt install -y docker.io
sudo usermod -aG docker $USER
docker --version

# Install Docker Compose
echo "Step 7: Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Install Git LFS
echo "Step 8: Installing Git LFS..."
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt install -y git-lfs
git lfs --version

# Verify jq
echo "Step 9: Verifying jq installation..."
jq --version

# Create project directory
echo "Step 10: Creating project directory..."
mkdir -p ~/mlops-platform
cd ~/mlops-platform

# Setup Python virtual environment
echo "Step 11: Setting up Python virtual environment..."
PYTHON_CMD=$(command -v python3.11 || command -v python3)
$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
echo "Virtual environment created at ~/mlops-platform/venv"

# Verify installations
echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo "AWS CLI: $(aws --version)"
echo "Git: $(git --version)"
echo "Python: $(python3 --version)"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not found')"
echo "npm: $(npm --version 2>/dev/null || echo 'Not found')"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "Git LFS: $(git lfs --version)"
echo "jq: $(jq --version)"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials:"
echo "   aws configure"
echo ""
echo "2. Clone the repository:"
echo "   cd ~/mlops-platform"
echo "   git clone https://github.com/your-org/mlops-platform.git"
echo "   cd mlops-platform"
echo ""
echo "3. Activate virtual environment:"
echo "   source ~/mlops-platform/venv/bin/activate"
echo ""
echo "4. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "5. Install frontend dependencies:"
echo "   cd frontend && npm install && cd .."
echo ""
echo "6. Run prerequisites check:"
echo "   chmod +x prereq.sh"
echo "   ./prereq.sh"
echo ""
echo "7. Deploy the platform:"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh --full-cloudfront"
echo ""
echo "Note: You may need to log out and log back in for Docker permissions."
echo "=========================================="