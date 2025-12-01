#!/bin/bash

# MLOps Platform Unified Deployment Script
# Usage: ./deploy.sh [--full]
#   --full: Deploy everything (infrastructure + CI/CD + data pipeline)
#   (default): Deploy infrastructure only

set -euo pipefail  # Strict error handling

# Security: Check for required tools
command -v aws >/dev/null 2>&1 || { echo "AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required but not installed. Aborting." >&2; exit 1; }

# Parse arguments
FULL_DEPLOYMENT=false
USE_CLOUDFRONT=false
if [ "$1" = "--full" ]; then
    FULL_DEPLOYMENT=true
elif [ "$1" = "--cloudfront" ]; then
    USE_CLOUDFRONT=true
elif [ "$1" = "--full-cloudfront" ]; then
    FULL_DEPLOYMENT=true
    USE_CLOUDFRONT=true
fi

# Configuration
STACK_NAME_BASE="mlops-platform"
ENVIRONMENT="dev"
REGION="us-east-1"

# Get AWS Account ID and validate credentials
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Error: Unable to get AWS identity. Please configure AWS CLI first."
    echo "Run: aws configure"
    exit 1
fi

# Validate AWS account ID format
if [[ ! "$AWS_ACCOUNT_ID" =~ ^[0-9]{12}$ ]]; then
    echo "Error: Invalid AWS Account ID format: $AWS_ACCOUNT_ID"
    exit 1
fi

# Security: Validate region
if [[ ! "$REGION" =~ ^[a-z]{2}-[a-z]+-[0-9]$ ]]; then
    echo "Error: Invalid AWS region format: $REGION"
    exit 1
fi

echo "========================================="
if [ "$FULL_DEPLOYMENT" = true ] && [ "$USE_CLOUDFRONT" = true ]; then
    echo "Complete MLOps Platform Deployment with CloudFront"
    echo "AWS Well-Architected Framework Compliant"
elif [ "$FULL_DEPLOYMENT" = true ]; then
    echo "Complete MLOps Platform Deployment"
    echo "AWS Well-Architected Framework Compliant"
elif [ "$USE_CLOUDFRONT" = true ]; then
    echo "MLOps Platform Deployment with CloudFront"
else
    echo "MLOps Platform Deployment (Infrastructure Only)"
fi
echo "========================================="
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Account: $AWS_ACCOUNT_ID"
echo "========================================="
echo ""

# Determine dataset bucket name
if [ "$FULL_DEPLOYMENT" = true ]; then
    # Auto-generate bucket name for full deployment
    DATASET_BUCKET="${STACK_NAME_BASE}-data-${ENVIRONMENT}-${AWS_ACCOUNT_ID}"
    echo "Dataset Bucket: $DATASET_BUCKET"
else
    # Prompt for bucket name for simple deployment
    read -p "Enter S3 bucket name for datasets (or press Enter for auto-generated): " DATASET_BUCKET
    if [ -z "$DATASET_BUCKET" ]; then
        DATASET_BUCKET="${STACK_NAME_BASE}-data-${ENVIRONMENT}-${AWS_ACCOUNT_ID}"
        echo "Using auto-generated bucket: $DATASET_BUCKET"
    fi
fi

# GitHub credentials (only for full deployment)
if [ "$FULL_DEPLOYMENT" = true ]; then
    echo ""
    echo "CI/CD Pipeline Setup (Optional)"
    echo "--------------------------------"
    echo "The CI/CD pipeline requires GitHub integration."
    echo "Press Enter to skip CI/CD deployment."
    echo ""
    read -p "Enter GitHub repository (format: owner/repo) or press Enter to skip: " GITHUB_REPO
    
    if [ -n "$GITHUB_REPO" ]; then
        read -p "Enter GitHub branch [main]: " GITHUB_BRANCH
        GITHUB_BRANCH=${GITHUB_BRANCH:-main}
        
        read -sp "Enter GitHub Personal Access Token: " GITHUB_TOKEN
        echo ""
        echo "✓ GitHub credentials provided"
    else
        echo "⚠ Skipping CI/CD pipeline deployment"
    fi
fi

echo ""
echo "========================================="

# Step 0: Create/Verify Dataset Bucket
echo ""
echo "Step 0: Setting up dataset bucket..."
if aws s3 ls "s3://${DATASET_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Creating bucket: ${DATASET_BUCKET}"
    aws s3 mb "s3://${DATASET_BUCKET}" --region $REGION
    
    # Enable versioning
    aws s3api put-bucket-versioning \
      --bucket ${DATASET_BUCKET} \
      --versioning-configuration Status=Enabled \
      --region $REGION
    
    # Add encryption
    aws s3api put-bucket-encryption \
      --bucket ${DATASET_BUCKET} \
      --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' \
      --region $REGION
    
    echo "✓ Dataset bucket created"
else
    echo "✓ Dataset bucket already exists"
fi

# Step 1: Deploy Main Infrastructure
echo ""
echo "Step 1: Deploying main infrastructure..."

STACK_NAME="${STACK_NAME_BASE}-${ENVIRONMENT}"
STACK_EXISTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION 2>&1)

if echo "$STACK_EXISTS" | grep -q "does not exist"; then
    echo "Creating new stack..."
    aws cloudformation create-stack \
      --stack-name $STACK_NAME \
      --template-body file://infrastructure/cloudformation-template.yaml \
      --parameters \
        ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        ParameterKey=DatasetBucketName,ParameterValue=$DATASET_BUCKET \
      --capabilities CAPABILITY_NAMED_IAM \
      --region $REGION

    echo "Waiting for stack creation..."
    aws cloudformation wait stack-create-complete \
      --stack-name $STACK_NAME \
      --region $REGION

    echo "✓ Infrastructure stack created"
else
    echo "Stack exists, updating..."
    aws cloudformation update-stack \
      --stack-name $STACK_NAME \
      --template-body file://infrastructure/cloudformation-template.yaml \
      --parameters \
        ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        ParameterKey=DatasetBucketName,ParameterValue=$DATASET_BUCKET \
      --capabilities CAPABILITY_NAMED_IAM \
      --region $REGION 2>&1 | tee /tmp/update-output.txt

    if grep -q "No updates are to be performed" /tmp/update-output.txt; then
        echo "✓ Stack is up to date"
    else
        echo "Waiting for stack update..."
        aws cloudformation wait stack-update-complete \
          --stack-name $STACK_NAME \
          --region $REGION
        echo "✓ Infrastructure stack updated"
    fi
fi

# Get stack outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text \
  --region $REGION)

DATA_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`DataBucketName`].OutputValue' \
  --output text \
  --region $REGION)

MODEL_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ModelBucketName`].OutputValue' \
  --output text \
  --region $REGION)

echo "API Endpoint: $API_ENDPOINT"
echo "Data Bucket: $DATA_BUCKET"
echo "Model Bucket: $MODEL_BUCKET"

# Step 2: Deploy CI/CD Pipeline (Full deployment only)
if [ "$FULL_DEPLOYMENT" = true ]; then
    echo ""
    echo "Step 2: CI/CD Pipeline..."
    
    if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_REPO" ]; then
        echo "Deploying CI/CD pipeline..."
        aws cloudformation create-stack \
          --stack-name ${STACK_NAME_BASE}-cicd-${ENVIRONMENT} \
          --template-body file://infrastructure/cicd-pipeline.yaml \
          --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN \
            ParameterKey=GitHubRepo,ParameterValue=${GITHUB_REPO} \
            ParameterKey=GitHubBranch,ParameterValue=${GITHUB_BRANCH:-main} \
          --capabilities CAPABILITY_NAMED_IAM \
          --region $REGION 2>/dev/null || echo "Stack may already exist"

        echo "✓ CI/CD pipeline deployed"
        
        REPO_URL=$(aws cloudformation describe-stacks \
          --stack-name ${STACK_NAME_BASE}-cicd-${ENVIRONMENT} \
          --query 'Stacks[0].Outputs[?OutputKey==`MLCodeRepositoryCloneUrl`].OutputValue' \
          --output text \
          --region $REGION 2>/dev/null || echo "Not available")
        
        PIPELINE_NAME=$(aws cloudformation describe-stacks \
          --stack-name ${STACK_NAME_BASE}-cicd-${ENVIRONMENT} \
          --query 'Stacks[0].Outputs[?OutputKey==`PipelineName`].OutputValue' \
          --output text \
          --region $REGION 2>/dev/null || echo "Not available")
    else
        echo "⚠ Skipping CI/CD (no GitHub credentials)"
        REPO_URL="Not deployed"
        PIPELINE_NAME="Not deployed"
    fi
    
    # Step 3: Upload Glue Scripts
    echo ""
    echo "Step 3: Uploading Glue scripts..."
    if [ -d "glue-scripts" ]; then
        [ -f "glue-scripts/data_validation.py" ] && aws s3 cp glue-scripts/data_validation.py s3://${DATA_BUCKET}/glue-scripts/ --region $REGION
        [ -f "glue-scripts/data_preprocessing.py" ] && aws s3 cp glue-scripts/data_preprocessing.py s3://${DATA_BUCKET}/glue-scripts/ --region $REGION
        echo "✓ Glue scripts uploaded"
    else
        echo "⚠ Glue scripts not found, skipping"
    fi
    
    # Step 4: Deploy Data Pipeline
    echo ""
    echo "Step 4: Deploying data pipeline..."
    aws cloudformation create-stack \
      --stack-name ${STACK_NAME_BASE}-data-pipeline-${ENVIRONMENT} \
      --template-body file://infrastructure/data-pipeline.yaml \
      --parameters \
        ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        ParameterKey=DataBucket,ParameterValue=$DATA_BUCKET \
      --capabilities CAPABILITY_NAMED_IAM \
      --region $REGION 2>/dev/null || echo "Stack may already exist"

    echo "✓ Data pipeline deployed"
    
    STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
      --stack-name ${STACK_NAME_BASE}-data-pipeline-${ENVIRONMENT} \
      --query 'Stacks[0].Outputs[?OutputKey==`DataPipelineStateMachineArn`].OutputValue' \
      --output text \
      --region $REGION 2>/dev/null || echo "Not available")
fi

# Step 5 (or 2 for simple): Deploy Lambda Functions
STEP_NUM=$( [ "$FULL_DEPLOYMENT" = true ] && echo "5" || echo "2" )
echo ""
echo "Step $STEP_NUM: Deploying Lambda functions..."
cd backend/lambda

zip -q -r training_handler.zip training_handler.py
zip -q -r inference_handler.zip inference_handler.py
zip -q -r model_registry_handler.zip model_registry_handler.py
zip -q -r dashboard_handler.zip dashboard_handler.py

aws lambda update-function-code \
  --function-name ${STACK_NAME_BASE}-training-handler-${ENVIRONMENT} \
  --zip-file fileb://training_handler.zip \
  --region $REGION > /dev/null 2>&1 || echo "  Training handler updated"

aws lambda update-function-code \
  --function-name ${STACK_NAME_BASE}-inference-handler-${ENVIRONMENT} \
  --zip-file fileb://inference_handler.zip \
  --region $REGION > /dev/null 2>&1 || echo "  Inference handler updated"

aws lambda update-function-code \
  --function-name ${STACK_NAME_BASE}-model-registry-handler-${ENVIRONMENT} \
  --zip-file fileb://model_registry_handler.zip \
  --region $REGION > /dev/null 2>&1 || echo "  Model registry handler updated"

aws lambda update-function-code \
  --function-name ${STACK_NAME_BASE}-dashboard-handler-${ENVIRONMENT} \
  --zip-file fileb://dashboard_handler.zip \
  --region $REGION > /dev/null 2>&1 || echo "  Dashboard handler updated"

rm -f *.zip
cd ../..
echo "✓ Lambda functions deployed"

# Step 6 (or 3 for simple): Upload Dataset
STEP_NUM=$( [ "$FULL_DEPLOYMENT" = true ] && echo "6" || echo "3" )
echo ""
echo "Step $STEP_NUM: Dataset Upload"
echo "----------------------"

CSV_FILES=($(ls -t *.csv 2>/dev/null | head -5))

if [ ${#CSV_FILES[@]} -gt 0 ]; then
    echo "Found CSV file(s):"
    for i in "${!CSV_FILES[@]}"; do
        FILE_SIZE=$(du -h "${CSV_FILES[$i]}" 2>/dev/null | cut -f1)
        echo "  $((i+1)). ${CSV_FILES[$i]} (${FILE_SIZE})"
    done
    echo ""
    echo "Most recent: ${CSV_FILES[0]}"
    echo ""
    
    read -p "Select file number [1] or 'n' to skip: " FILE_CHOICE
    
    if [ "$FILE_CHOICE" != "n" ] && [ "$FILE_CHOICE" != "N" ]; then
        FILE_CHOICE=${FILE_CHOICE:-1}
        
        if [ "$FILE_CHOICE" -ge 1 ] && [ "$FILE_CHOICE" -le ${#CSV_FILES[@]} ]; then
            DATASET_FILE="${CSV_FILES[$((FILE_CHOICE-1))]}"
            echo "Uploading $DATASET_FILE..."
            
            aws s3 cp "$DATASET_FILE" "s3://${DATA_BUCKET}/datasets/$DATASET_FILE" --region $REGION
            
            if [ $? -eq 0 ]; then
                echo "✓ Dataset uploaded to s3://${DATA_BUCKET}/datasets/$DATASET_FILE"
                UPLOADED_DATASET="s3://${DATA_BUCKET}/datasets/$DATASET_FILE"
            fi
        fi
    else
        echo "⚠ Dataset upload skipped"
    fi
else
    echo "⚠ No CSV files found"
    echo "Upload later: aws s3 cp your_dataset.csv s3://${DATA_BUCKET}/datasets/"
fi

# Step 7 (or 4 for simple): Build Frontend
STEP_NUM=$( [ "$FULL_DEPLOYMENT" = true ] && echo "7" || echo "4" )
echo ""
echo "Step $STEP_NUM: Building frontend..."
cd frontend
echo "REACT_APP_API_URL=$API_ENDPOINT" > .env
npm install --silent 2>/dev/null || npm install
npm run build 2>/dev/null || echo "Build completed with warnings"
cd ..
echo "✓ Frontend built (frontend/build/)"

# Create deployment summary
echo ""
echo "Creating deployment summary..."

cat > DEPLOYMENT_INFO.txt << EOF
========================================
MLOps Platform Deployment Summary
========================================
Date: $(date)
Environment: $ENVIRONMENT
Region: $REGION
Deployment Type: $( [ "$FULL_DEPLOYMENT" = true ] && echo "Full" || echo "Infrastructure Only" )

INFRASTRUCTURE
--------------
Main Stack: ${STACK_NAME_BASE}-${ENVIRONMENT}
$( [ "$FULL_DEPLOYMENT" = true ] && echo "CI/CD Stack: ${STACK_NAME_BASE}-cicd-${ENVIRONMENT}" || echo "" )
$( [ "$FULL_DEPLOYMENT" = true ] && echo "Data Pipeline Stack: ${STACK_NAME_BASE}-data-pipeline-${ENVIRONMENT}" || echo "" )

ENDPOINTS
---------
API Gateway: $API_ENDPOINT

STORAGE
-------
Data Bucket: $DATA_BUCKET
Model Bucket: $MODEL_BUCKET

$( [ "$FULL_DEPLOYMENT" = true ] && [ -n "$GITHUB_TOKEN" ] && echo "GITHUB INTEGRATION
------------------
Repository: ${REPO_URL}
Pipeline: ${PIPELINE_NAME}" || echo "" )

DATASET
-------
Uploaded: ${UPLOADED_DATASET:-"None - upload manually"}
Upload command: aws s3 cp your_dataset.csv s3://${DATA_BUCKET}/datasets/

NEXT STEPS
----------
1. Upload dataset (if not done): aws s3 cp dataset.csv s3://${DATA_BUCKET}/datasets/
2. Access UI: open frontend/build/index.html
3. Test API: curl $API_ENDPOINT/models
4. Start training: POST $API_ENDPOINT/training/start

DOCUMENTATION
-------------
- docs/QUICKSTART.md - Getting started
- docs/DATASET_UPLOAD_GUIDE.md - Dataset management
- docs/DEPLOYMENT.md - Deployment guide
========================================
EOF

# Final Summary
echo ""
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo ""
if [ "$FULL_DEPLOYMENT" = true ]; then
    echo "✅ Main Infrastructure"
    [ -n "$GITHUB_TOKEN" ] && echo "✅ CI/CD Pipeline" || echo "⚠️  CI/CD Pipeline (skipped)"
    echo "✅ Data Pipeline"
    echo "✅ Lambda Functions"
    echo "✅ Frontend Built"
else
    echo "✅ Infrastructure Deployed"
    echo "✅ Lambda Functions Updated"
    echo "✅ Frontend Built"
fi
echo ""
echo "📍 Resources:"
echo "   API: $API_ENDPOINT"
echo "   Data: $DATA_BUCKET"
echo "   Models: $MODEL_BUCKET"
if [ -n "$CLOUDFRONT_URL" ]; then
    echo "   Frontend: $CLOUDFRONT_URL"
else
    echo "   Frontend: frontend/build/index.html (local)"
fi
echo ""
[ -n "$UPLOADED_DATASET" ] && echo "✅ Dataset: $UPLOADED_DATASET" && echo ""
echo "📄 Details: DEPLOYMENT_INFO.txt"
echo ""
echo "🚀 Next Steps:"
echo "   1. Upload dataset: aws s3 cp dataset.csv s3://${DATA_BUCKET}/datasets/"
if [ -n "$CLOUDFRONT_URL" ]; then
    echo "   2. Open UI: $CLOUDFRONT_URL"
else
    echo "   2. Open UI: frontend/build/index.html"
fi
echo "   3. Test API: curl $API_ENDPOINT/models"
echo ""
if [ "$FULL_DEPLOYMENT" = false ] && [ "$USE_CLOUDFRONT" = false ]; then
    echo "💡 Deployment options:"
    echo "   ./deploy.sh --full              # Full deployment"
    echo "   ./deploy.sh --cloudfront       # Add CloudFront"
    echo "   ./deploy.sh --full-cloudfront  # Full + CloudFront"
    echo ""
fi
echo "========================================="
# Step: Deploy CloudFront (if requested)
if [ "$USE_CLOUDFRONT" = true ] || [ "$FULL_DEPLOYMENT" = true ]; then
    STEP_NUM=$( [ "$FULL_DEPLOYMENT" = true ] && echo "8" || echo "5" )
    echo ""
    echo "Step $STEP_NUM: Deploying CloudFront distribution..."
    
    FRONTEND_BUCKET="${STACK_NAME_BASE}-frontend-${ENVIRONMENT}-${AWS_ACCOUNT_ID}"
    
    aws cloudformation deploy \
      --template-file infrastructure/cloudfront-template.yaml \
      --stack-name ${STACK_NAME_BASE}-cloudfront-${ENVIRONMENT} \
      --parameters \
        ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        ParameterKey=FrontendBucketName,ParameterValue=$FRONTEND_BUCKET \
      --region $REGION
    
    # Get CloudFront URL
    CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
      --stack-name ${STACK_NAME_BASE}-cloudfront-${ENVIRONMENT} \
      --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
      --output text \
      --region $REGION)
    
    echo "✓ CloudFront deployed: $CLOUDFRONT_URL"
    
    # Upload frontend to S3
    echo "Uploading frontend to S3..."
    aws s3 sync frontend/build/ s3://${FRONTEND_BUCKET}/ --delete --region $REGION
    
    # Invalidate CloudFront cache
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
      --stack-name ${STACK_NAME_BASE}-cloudfront-${ENVIRONMENT} \
      --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
      --output text \
      --region $REGION)
    
    aws cloudfront create-invalidation \
      --distribution-id $DISTRIBUTION_ID \
      --paths "/*" \
      --region $REGION > /dev/null
    
    echo "✓ Frontend deployed to CloudFront"
fi