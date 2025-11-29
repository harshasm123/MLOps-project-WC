#!/bin/bash

# MLOps Platform Deployment Script
# This script deploys the entire MLOps platform to AWS

set -e

# Prompt for dataset bucket name
echo "========================================="
echo "MLOps Platform Deployment"
echo "========================================="
echo ""
read -p "Enter the S3 bucket name for datasets (e.g., my-mlops-datasets): " DATASET_BUCKET

# Validate bucket name
if [ -z "$DATASET_BUCKET" ]; then
    echo "Error: Dataset bucket name cannot be empty"
    exit 1
fi

# Configuration
STACK_NAME="mlops-platform-dev"
ENVIRONMENT="dev"
REGION="us-east-1"

# Step 0: Create Dataset Bucket
echo ""
echo "Step 0: Creating dataset bucket..."
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
    
    echo "✓ Dataset bucket created successfully"
else
    echo "✓ Dataset bucket already exists"
fi

# Step 1: Deploy CloudFormation Stack
echo ""
echo "Step 1: Deploying CloudFormation stack..."
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
    ParameterKey=DatasetBucketName,ParameterValue=$DATASET_BUCKET \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $REGION

echo "✓ CloudFormation stack created successfully"

# Step 2: Get Stack Outputs
echo ""
echo "Step 2: Retrieving stack outputs..."
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

# Step 3: Package and Deploy Lambda Functions
echo ""
echo "Step 3: Deploying Lambda functions..."
cd backend/lambda

# Package functions
echo "Packaging Lambda functions..."
zip -q -r training_handler.zip training_handler.py
zip -q -r inference_handler.zip inference_handler.py
zip -q -r model_registry_handler.zip model_registry_handler.py

# Update functions
echo "Updating training handler..."
aws lambda update-function-code \
  --function-name mlops-platform-training-handler-$ENVIRONMENT \
  --zip-file fileb://training_handler.zip \
  --region $REGION > /dev/null

echo "Updating inference handler..."
aws lambda update-function-code \
  --function-name mlops-platform-inference-handler-$ENVIRONMENT \
  --zip-file fileb://inference_handler.zip \
  --region $REGION > /dev/null

echo "Updating model registry handler..."
aws lambda update-function-code \
  --function-name mlops-platform-model-registry-handler-$ENVIRONMENT \
  --zip-file fileb://model_registry_handler.zip \
  --region $REGION > /dev/null

# Cleanup
rm -f *.zip

cd ../..
echo "✓ Lambda functions deployed successfully"

# Step 4: Upload Dataset
echo ""
echo "Step 4: Uploading dataset to S3..."
if [ -f "diabetic_data.csv" ]; then
    aws s3 cp diabetic_data.csv s3://${DATA_BUCKET}/datasets/diabetic_data.csv --region $REGION
    echo "✓ Dataset uploaded successfully"
else
    echo "⚠ Warning: diabetic_data.csv not found. Please upload manually."
fi

# Step 5: Build Frontend
echo ""
echo "Step 5: Building React frontend..."
cd frontend

# Create .env file with API endpoint
echo "REACT_APP_API_URL=$API_ENDPOINT" > .env

# Install dependencies and build
echo "Installing dependencies..."
npm install --silent

echo "Building production bundle..."
npm run build

cd ..
echo "✓ Frontend built successfully"

# Step 6: Summary
echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "API Endpoint: $API_ENDPOINT"
echo "Data Bucket: $DATA_BUCKET"
echo "Model Bucket: $MODEL_BUCKET"
echo ""
echo "Next Steps:"
echo "1. Access the frontend at: frontend/build/index.html"
echo "2. Test the API: curl $API_ENDPOINT/models"
echo "3. Start a training job through the UI or API"
echo ""
echo "To deploy frontend to S3:"
echo "  aws s3 sync frontend/build/ s3://your-frontend-bucket/ --acl public-read"
echo ""
echo "To view logs:"
echo "  aws logs tail /aws/lambda/mlops-platform-training-handler-$ENVIRONMENT --follow"
echo ""
echo "========================================="
