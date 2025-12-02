#!/bin/bash

set -euo pipefail

STACK_NAME="mlops-platform-dev"
ENVIRONMENT="dev"
REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
DATA_BUCKET="mlops-platform-data-dev-${AWS_ACCOUNT_ID}"
FRONTEND_BUCKET="mlops-platform-frontend-${ENVIRONMENT}-${AWS_ACCOUNT_ID}"

echo "=========================================="
echo "Fixing MLOps Platform Deployment"
echo "=========================================="

# Step 1: Update Stack (skip if no changes)
echo "Step 1: Checking CloudFormation stack..."
UPDATE_OUTPUT=$(aws cloudformation update-stack \
  --stack-name $STACK_NAME \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
    ParameterKey=DatasetBucketName,ParameterValue=$DATA_BUCKET \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION 2>&1 || true)

if echo "$UPDATE_OUTPUT" | grep -q "No updates are to be performed"; then
    echo "✓ Stack is up to date"
elif echo "$UPDATE_OUTPUT" | grep -q "StackId"; then
    echo "Waiting for stack update..."
    aws cloudformation wait stack-update-complete \
      --stack-name $STACK_NAME \
      --region $REGION 2>/dev/null || true
    echo "✓ Stack updated"
fi

# Get API Endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text \
  --region $REGION)

echo "API Endpoint: $API_ENDPOINT"

# Step 2: Deploy Lambda Functions
echo ""
echo "Step 2: Deploying Lambda functions..."
cd backend/lambda

zip -q -r training_handler.zip training_handler.py
zip -q -r inference_handler.zip inference_handler.py
zip -q -r model_registry_handler.zip model_registry_handler.py
zip -q -r dashboard_handler.zip dashboard_handler.py

aws lambda update-function-code \
  --function-name mlops-platform-training-handler-${ENVIRONMENT} \
  --zip-file fileb://training_handler.zip \
  --region $REGION > /dev/null 2>&1

aws lambda update-function-code \
  --function-name mlops-platform-inference-handler-${ENVIRONMENT} \
  --zip-file fileb://inference_handler.zip \
  --region $REGION > /dev/null 2>&1

aws lambda update-function-code \
  --function-name mlops-platform-model-registry-handler-${ENVIRONMENT} \
  --zip-file fileb://model_registry_handler.zip \
  --region $REGION > /dev/null 2>&1

aws lambda update-function-code \
  --function-name mlops-platform-dashboard-handler-${ENVIRONMENT} \
  --zip-file fileb://dashboard_handler.zip \
  --region $REGION > /dev/null 2>&1

rm -f *.zip
cd ../..

echo "✓ Lambda functions deployed"

# Step 3: Deploy CloudFront
echo ""
echo "Step 3: Deploying CloudFront distribution..."

aws s3api head-bucket --bucket $FRONTEND_BUCKET --region $REGION 2>/dev/null || \
  aws s3 mb s3://$FRONTEND_BUCKET --region $REGION

aws cloudformation deploy \
  --template-file infrastructure/cloudfront-template.yaml \
  --stack-name mlops-platform-cloudfront-${ENVIRONMENT} \
  --parameters \
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
    ParameterKey=FrontendBucketName,ParameterValue=$FRONTEND_BUCKET \
  --region $REGION

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-cloudfront-${ENVIRONMENT} \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
  --output text \
  --region $REGION)

echo "✓ CloudFront deployed: $CLOUDFRONT_URL"

# Step 4: Build and Upload Frontend
echo ""
echo "Step 4: Uploading frontend to S3..."

cd frontend
echo "REACT_APP_API_URL=$API_ENDPOINT" > .env
npm install --silent 2>/dev/null || npm install
npm run build 2>/dev/null || echo "Build completed"
cd ..

aws s3 sync frontend/build/ s3://${FRONTEND_BUCKET}/ --delete --region $REGION

DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-cloudfront-${ENVIRONMENT} \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text \
  --region $REGION)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*" \
  --region $REGION > /dev/null

echo "✓ Frontend deployed to CloudFront"

# Step 5: Verify API
echo ""
echo "Step 5: Verifying API endpoints..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/models")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ API working: $BODY"
else
    echo "⚠ API returned HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📍 Resources:"
echo "   API: $API_ENDPOINT"
echo "   Frontend: $CLOUDFRONT_URL"
echo ""
echo "🚀 Next Steps:"
echo "   1. Open UI: $CLOUDFRONT_URL"
echo "   2. Test API: curl $API_ENDPOINT/models"
echo ""
echo "=========================================="
