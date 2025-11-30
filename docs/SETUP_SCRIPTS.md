# Setup Scripts Guide

## Overview

This project includes two setup scripts with different purposes:

## 1. `ec2-setup.sh` - Basic EC2 Setup

**Purpose:** Install only essential tools on a fresh EC2 instance

**What it installs:**
- ✅ Git
- ✅ unzip
- ✅ wget
- ✅ curl
- ✅ AWS CLI

**When to use:**
- Fresh EC2 instance
- Minimal setup needed
- Before cloning the repository

**Usage:**
```bash
# On EC2 instance
chmod +x ec2-setup.sh
./ec2-setup.sh
```

**What it does NOT install:**
- Python packages
- Node.js
- Docker
- Project dependencies

## 2. `prereq.sh` - Full Prerequisites Setup

**Purpose:** Check and install all development dependencies

**What it checks/installs:**
- ✅ AWS CLI
- ✅ AWS credentials
- ✅ Python 3.9+
- ✅ pip
- ✅ Node.js 18+
- ✅ npm
- ✅ Git
- ✅ jq (optional)
- ✅ Docker (optional)
- ✅ Python dependencies (from requirements.txt)
- ✅ AWS service permissions

**When to use:**
- Local development machine
- After running ec2-setup.sh on EC2
- Before deploying the platform
- To verify all prerequisites

**Usage:**
```bash
# After cloning repository
chmod +x prereq.sh
./prereq.sh
```

## Recommended Workflow

### For EC2 Deployment

```bash
# Step 1: SSH into EC2
ssh -i your-key.pem ubuntu@<ec2-ip>

# Step 2: Run basic setup
wget https://raw.githubusercontent.com/your-repo/main/ec2-setup.sh
chmod +x ec2-setup.sh
./ec2-setup.sh

# Step 3: Configure AWS
aws configure

# Step 4: Clone repository
git clone https://github.com/your-repo/mlops-platform.git
cd mlops-platform

# Step 5: Run full prerequisites
chmod +x prereq.sh
./prereq.sh

# Step 6: Deploy
./deploy-complete.sh
```

### For Local Development

```bash
# Step 1: Clone repository
git clone https://github.com/your-repo/mlops-platform.git
cd mlops-platform

# Step 2: Run prerequisites check
chmod +x prereq.sh
./prereq.sh

# Step 3: Deploy (if all checks pass)
./deploy-complete.sh
```

## Script Comparison

| Feature | ec2-setup.sh | prereq.sh |
|---------|--------------|-----------|
| **Purpose** | Basic tools only | Full dev environment |
| **Git** | ✅ Installs | ✅ Checks |
| **AWS CLI** | ✅ Installs | ✅ Checks |
| **Python** | ❌ | ✅ Checks & installs deps |
| **Node.js** | ❌ | ✅ Checks |
| **Docker** | ❌ | ✅ Checks (optional) |
| **AWS Credentials** | ❌ | ✅ Verifies |
| **AWS Permissions** | ❌ | ✅ Checks |
| **Project Dependencies** | ❌ | ✅ Installs |
| **Run Time** | ~2-3 minutes | ~5-10 minutes |
| **Disk Space** | ~500MB | ~2-3GB |

## Troubleshooting

### ec2-setup.sh Issues

**Problem:** "unzip: command not found"
```bash
# This should not happen anymore, but if it does:
sudo apt-get install -y unzip  # Ubuntu/Debian
sudo yum install -y unzip      # Amazon Linux/RHEL
```

**Problem:** "No space left on device"
```bash
# Check disk space
df -h

# Clean up if needed
sudo apt-get clean
sudo apt-get autoremove -y
```

### prereq.sh Issues

**Problem:** "AWS credentials not configured"
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (json)
```

**Problem:** "Python version too old"
```bash
# Ubuntu 24.04 - Python 3.12 is default
sudo apt-get install -y python3.12

# Ubuntu 22.04 - Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11
```

**Problem:** "Node.js version too old"
```bash
# Install Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Problem:** "AWS service not accessible"
```bash
# Check IAM permissions
aws iam get-user

# Verify you have required permissions:
# - SageMaker: sagemaker:*
# - S3: s3:*
# - Lambda: lambda:*
# - CloudFormation: cloudformation:*
```

## Environment-Specific Notes

### Ubuntu 24.04
- Uses Python 3.12 by default
- Has apt_pkg issues (handled automatically)
- Requires `--break-system-packages` for pip (handled automatically)

### Amazon Linux 2023
- Uses Python 3.11 by default
- Uses yum package manager
- No special handling needed

### Ubuntu 22.04
- Uses Python 3.10 by default
- May need to install Python 3.11+ manually
- Standard apt package manager

## Additional Resources

- **AWS CLI Documentation:** https://docs.aws.amazon.com/cli/
- **Node.js Installation:** https://nodejs.org/
- **Python Installation:** https://www.python.org/downloads/
- **Docker Installation:** https://docs.docker.com/get-docker/

## Support

If you encounter issues:

1. Check the error message carefully
2. Verify disk space: `df -h`
3. Check internet connectivity: `ping google.com`
4. Verify AWS credentials: `aws sts get-caller-identity`
5. Review logs in `/var/log/` (on Linux)

For deployment issues, see:
- `docs/DEPLOYMENT.md`
- `docs/QUICKSTART.md`
- `docs/BACKEND_ENHANCEMENTS.md`
