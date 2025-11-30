#!/bin/bash

# Prerequisites Checker and Setup Script for MLOps Platform
# This script checks and installs all required dependencies for local development
# For EC2 setup, use ec2-setup.sh instead

set -e

echo "========================================="
echo "MLOps Platform - Prerequisites Setup"
echo "========================================="
echo ""
echo "This script will check and install all required dependencies"
echo "for local development and deployment."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "Checking prerequisites..."
echo ""

# Check AWS CLI
echo "1. Checking AWS CLI..."
if command_exists aws; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
    print_status 0 "AWS CLI installed (version $AWS_VERSION)"
else
    print_status 1 "AWS CLI not found"
    echo "   Install: https://aws.amazon.com/cli/"
    echo "   Or run: pip install awscli"
    exit 1
fi

# Check AWS credentials
echo ""
echo "2. Checking AWS credentials..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_status 0 "AWS credentials configured (Account: $ACCOUNT_ID)"
else
    print_status 1 "AWS credentials not configured"
    echo "   Run: aws configure"
    exit 1
fi

# Check Python
echo ""
echo "3. Checking Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status 0 "Python installed (version $PYTHON_VERSION)"
    
    # Check if version is 3.9+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_status 0 "Python version is 3.9+ (required)"
    else
        print_warning "Python 3.9+ recommended (you have $PYTHON_VERSION)"
    fi
else
    print_status 1 "Python 3 not found"
    echo "   Install: https://www.python.org/downloads/"
    exit 1
fi

# Check pip
echo ""
echo "4. Checking pip..."
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_status 0 "pip installed (version $PIP_VERSION)"
else
    print_status 1 "pip not found"
    echo "   Install: python3 -m ensurepip"
    exit 1
fi

# Check Node.js (for frontend)
echo ""
echo "5. Checking Node.js..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status 0 "Node.js installed ($NODE_VERSION)"
    
    # Check if version is 18+
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_status 0 "Node.js version is 18+ (required)"
    else
        print_warning "Node.js 18+ recommended (you have $NODE_VERSION)"
    fi
else
    print_status 1 "Node.js not found"
    echo "   Install: https://nodejs.org/"
    echo "   Or run: brew install node (macOS)"
    exit 1
fi

# Check npm
echo ""
echo "6. Checking npm..."
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status 0 "npm installed (version $NPM_VERSION)"
else
    print_status 1 "npm not found (should come with Node.js)"
    exit 1
fi

# Check Git
echo ""
echo "7. Checking Git..."
if command_exists git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_status 0 "Git installed (version $GIT_VERSION)"
else
    print_status 1 "Git not found"
    echo "   Install: https://git-scm.com/"
    exit 1
fi

# Check jq (optional but useful)
echo ""
echo "8. Checking jq (optional)..."
if command_exists jq; then
    JQ_VERSION=$(jq --version | cut -d'-' -f2)
    print_status 0 "jq installed (version $JQ_VERSION)"
else
    print_warning "jq not found (optional, but recommended for JSON parsing)"
    echo "   Install: brew install jq (macOS) or apt-get install jq (Linux)"
fi

# Check Docker (optional for local testing)
echo ""
echo "9. Checking Docker (optional)..."
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_status 0 "Docker installed (version $DOCKER_VERSION)"
else
    print_warning "Docker not found (optional, but useful for local testing)"
    echo "   Install: https://www.docker.com/get-started"
fi

# Install Python dependencies
echo ""
echo "10. Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "   Installing from requirements.txt..."
    
    # Detect OS for PEP 668 handling
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
        OS_VERSION=$VERSION_ID
    fi
    
    # Handle Ubuntu/Debian PEP 668 restriction
    if [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
        echo "   Detected Ubuntu/Debian - using --break-system-packages flag"
        pip3 install --break-system-packages -r requirements.txt --quiet
        print_status $? "Python dependencies installed (with --break-system-packages)"
    else
        pip3 install -r requirements.txt --quiet
        print_status $? "Python dependencies installed"
    fi
else
    print_warning "requirements.txt not found, skipping Python dependencies"
fi

# Check AWS region
echo ""
echo "11. Checking AWS region..."
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    print_warning "AWS region not set, defaulting to us-east-1"
    export AWS_REGION="us-east-1"
else
    print_status 0 "AWS region set to $AWS_REGION"
fi

# Check required AWS services availability
echo ""
echo "12. Checking AWS service availability..."

# Check SageMaker
if aws sagemaker list-training-jobs --max-results 1 >/dev/null 2>&1; then
    print_status 0 "SageMaker accessible"
else
    print_warning "SageMaker not accessible (check IAM permissions)"
fi

# Check S3
if aws s3 ls >/dev/null 2>&1; then
    print_status 0 "S3 accessible"
else
    print_warning "S3 not accessible (check IAM permissions)"
fi

# Check Lambda
if aws lambda list-functions --max-items 1 >/dev/null 2>&1; then
    print_status 0 "Lambda accessible"
else
    print_warning "Lambda not accessible (check IAM permissions)"
fi

# Check CloudFormation
if aws cloudformation list-stacks --max-results 1 >/dev/null 2>&1; then
    print_status 0 "CloudFormation accessible"
else
    print_warning "CloudFormation not accessible (check IAM permissions)"
fi

# Summary
echo ""
echo "========================================="
echo "Prerequisites Check Complete!"
echo "========================================="
echo ""

# Check if GitHub is configured (optional)
echo "Optional: GitHub Configuration"
if git config --global user.name >/dev/null 2>&1; then
    GIT_USER=$(git config --global user.name)
    print_status 0 "Git user configured: $GIT_USER"
else
    print_warning "Git user not configured"
    echo "   Run: git config --global user.name 'Your Name'"
    echo "   Run: git config --global user.email 'your@email.com'"
fi

echo ""
echo "Next Steps:"
echo "1. Review AWS_WELL_ARCHITECTED.md for architecture details"
echo "2. Review GITOPS_GUIDE.md for deployment with GitHub"
echo "3. Run: ./deploy-complete.sh (to deploy everything)"
echo "   Or: ./deploy.sh (to deploy infrastructure only)"
echo ""
echo "For GitHub deployment:"
echo "1. Create GitHub repository"
echo "2. Set GitHub Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
echo "3. Push code to GitHub"
echo "4. GitHub Actions will deploy automatically"
echo ""
echo "========================================="
