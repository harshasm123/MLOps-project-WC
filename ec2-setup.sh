#!/bin/bash

# EC2 Basic Setup Script
# This script installs essential tools: git, unzip, wget, curl, Python, pip, AWS CLI
# For full development environment setup, use prereq.sh after this

set -e

echo "========================================="
echo "EC2 Basic Setup - Essential Tools Only"
echo "========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "✗ Cannot detect OS. /etc/os-release file not found."
    echo "   Troubleshooting:"
    echo "   - Ensure you are running on a supported Linux distribution"
    echo "   - Supported: Amazon Linux, Ubuntu, Debian, RHEL, CentOS"
    exit 1
fi

echo "Detected OS: $OS $VERSION"

# Validate OS is supported
SUPPORTED_OS=("amzn" "ubuntu" "debian" "rhel" "centos")
OS_SUPPORTED=false
for supported in "${SUPPORTED_OS[@]}"; do
    if [ "$OS" = "$supported" ]; then
        OS_SUPPORTED=true
        break
    fi
done

if [ "$OS_SUPPORTED" = false ]; then
    echo "✗ Unsupported OS: $OS"
    echo "   This script supports: Amazon Linux, Ubuntu, Debian, RHEL, CentOS"
    echo "   Troubleshooting:"
    echo "   - Use a supported Linux distribution"
    echo "   - For other distributions, install tools manually:"
    echo "     git, unzip, wget, curl, python3, python3-pip, AWS CLI"
    exit 1
fi

echo "✓ OS is supported"
echo ""

# Check available disk space
AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))
echo "Available disk space: ${AVAILABLE_GB}GB"
if [ "$AVAILABLE_GB" -lt 5 ]; then
    echo "⚠️  WARNING: Low disk space (${AVAILABLE_GB}GB available)"
    echo "   Recommended: At least 10GB free space"
    read -p "Continue anyway? (y/n): " CONTINUE_LOW_SPACE
    if [ "$CONTINUE_LOW_SPACE" != "y" ] && [ "$CONTINUE_LOW_SPACE" != "Y" ]; then
        echo "Exiting. Please increase disk space and try again."
        exit 1
    fi
fi
echo ""

# Fix Ubuntu 24.04 apt_pkg issue
if [ "$OS" = "ubuntu" ] && [ "$VERSION_ID" = "24.04" ]; then
    echo "Fixing Ubuntu 24.04 apt_pkg issue..."
    sudo rm -f /var/lib/command-not-found/commands.db.metadata 2>/dev/null || true
    export APT_LISTCHANGES_FRONTEND=none
    export DEBIAN_FRONTEND=noninteractive
fi

# Update system packages and install essential tools
echo "Step 1: Installing essential tools (git, unzip, wget, curl, zip)..."
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum update -y
    sudo yum install -y git unzip wget curl zip
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    # Fix apt_pkg issue on Ubuntu 24.04
    if [ "$VERSION_ID" = "24.04" ]; then
        sudo apt-get update -y 2>&1 | grep -v "apt_pkg" || true
        sudo apt-get install -y --reinstall python3-apt 2>&1 | grep -v "apt_pkg" || true
    else
        sudo apt-get update -y
    fi
    sudo apt-get upgrade -y
    sudo apt-get install -y git unzip wget curl zip
    # Clean up apt cache to free space
    sudo apt-get clean
    sudo apt-get autoremove -y
fi
echo "✓ Essential tools installed"

# Install Python and pip
echo ""
echo "Step 2: Installing Python and pip..."
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum install -y python3 python3-pip
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install -y python3 python3-pip
    # Clean up apt cache to free space
    sudo apt-get clean
    sudo apt-get autoremove -y
fi
echo "✓ Python and pip installed"

# Verify installations
echo ""
echo "Step 3: Verifying installations..."
if command -v git &> /dev/null; then
    echo "✓ Git installed ($(git --version))"
else
    echo "✗ Git installation failed"
    exit 1
fi

if command -v unzip &> /dev/null; then
    echo "✓ unzip installed"
else
    echo "✗ unzip installation failed"
    exit 1
fi

if command -v wget &> /dev/null; then
    echo "✓ wget installed"
else
    echo "✗ wget installation failed"
    exit 1
fi

if command -v curl &> /dev/null; then
    echo "✓ curl installed"
else
    echo "✗ curl installation failed"
    exit 1
fi

if command -v zip &> /dev/null; then
    echo "✓ zip installed"
else
    echo "✗ zip installation failed"
    exit 1
fi

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python installed (version $PYTHON_VERSION)"
else
    echo "✗ Python installation failed"
    exit 1
fi

if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ pip installed (version $PIP_VERSION)"
else
    echo "✗ pip installation failed"
    exit 1
fi

# Install AWS CLI
echo ""
echo "Step 4: Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    echo "✓ AWS CLI installed"
else
    echo "✓ AWS CLI already installed ($(aws --version))"
fi

# Summary
echo ""
echo "========================================="
echo "EC2 Basic Setup Complete!"
echo "========================================="
echo ""
echo "Installed Tools:"
echo "  ✓ Git $(git --version | cut -d' ' -f3)"
echo "  ✓ unzip"
echo "  ✓ zip"
echo "  ✓ wget"
echo "  ✓ curl"
echo "  ✓ Python $(python3 --version 2>&1 | cut -d' ' -f2)"
echo "  ✓ pip $(pip3 --version 2>&1 | cut -d' ' -f2)"
echo "  ✓ AWS CLI $(aws --version 2>&1 | cut -d' ' -f1)"
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure AWS credentials:"
echo "   aws configure"
echo ""
echo "2. Clone your repository:"
echo "   git clone <your-repo-url> mlops-platform"
echo "   cd mlops-platform"
echo ""
echo "3. Run full prerequisites setup:"
echo "   chmod +x prereq.sh"
echo "   ./prereq.sh"
echo ""
echo "4. Deploy the platform:"
echo "   ./deploy-complete.sh"
echo ""
echo "========================================="
