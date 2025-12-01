# EC2 Setup Guide for MLOps Platform

## Overview

This guide covers setting up an EC2 instance to run the MLOps Platform deployment scripts and development environment.

## Prerequisites

- AWS Account with appropriate permissions
- EC2 instance (t3.medium or larger recommended)
- Ubuntu 22.04 LTS or Amazon Linux 2

## Instance Setup

### Step 1: Launch EC2 Instance

```bash
# Recommended instance type
Instance Type: t3.medium or t3.large
AMI: Ubuntu 22.04 LTS or Amazon Linux 2
Storage: 50GB gp3
Security Group: Allow SSH (22), HTTP (80), HTTPS (443)
```

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 3: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 4: Install Dependencies

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Git
sudo apt install -y git

# jq (for JSON parsing)
sudo apt install -y jq
```

### Step 5: Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (us-east-1)
# Enter default output format (json)
```

### Step 6: Clone Repository

```bash
git clone https://github.com/your-org/mlops-platform.git
cd mlops-platform
```

### Step 7: Install Python Dependencies

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 8: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Deployment

### Run Prerequisites Check

```bash
chmod +x prereq.sh
./prereq.sh
```

### Deploy Platform

```bash
chmod +x deploy.sh

# Full deployment with CloudFront
./deploy.sh --full-cloudfront

# Or infrastructure only
./deploy.sh
```

## Monitoring

### View Logs

```bash
# CloudFormation events
aws cloudformation describe-stack-events --stack-name mlops-platform-dev

# Lambda logs
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow

# SageMaker jobs
aws sagemaker list-training-jobs --max-results 10
```

## Cleanup

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name mlops-platform-dev

# Delete S3 buckets
aws s3 rm s3://your-bucket --recursive
aws s3 rb s3://your-bucket
```

## Troubleshooting

### AWS CLI Not Found
```bash
which aws
# If not found, reinstall AWS CLI
```

### Python Version Issues
```bash
python3.11 --version
# Should be 3.11.x
```

### Node.js Version Issues
```bash
node --version
# Should be v18.x or higher
```

### Permission Denied
```bash
chmod +x deploy.sh prereq.sh
```

## Best Practices

1. **Use IAM Roles**: Attach IAM role to EC2 instead of using access keys
2. **Security Groups**: Restrict SSH access to your IP
3. **Monitoring**: Enable CloudWatch monitoring
4. **Backups**: Regular snapshots of EBS volumes
5. **Cost**: Use spot instances for non-production environments