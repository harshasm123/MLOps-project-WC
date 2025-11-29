# MLOps Platform Deployment Guide

This guide explains how to deploy the MLOps Platform to AWS using CloudFormation, Lambda, API Gateway, and SageMaker.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured with credentials
3. Node.js 18+ (for React frontend)
4. Python 3.11+ (for Lambda functions)

## Architecture Overview

The platform consists of:
- **Frontend**: React application hosted on S3 + CloudFront
- **Backend**: Lambda functions behind API Gateway
- **ML Infrastructure**: SageMaker for training and inference
- **Storage**: S3 buckets for data and models
- **Database**: DynamoDB for model registry

## Deployment Steps

### Step 1: Deploy Infrastructure

Deploy the CloudFormation stack:

```bash
aws cloudformation create-stack \
  --stack-name mlops-platform-dev \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

Wait for stack creation:

```bash
aws cloudformation wait stack-create-complete \
  --stack-name mlops-platform-dev \
  --region us-east-1
```

Get the API endpoint:

```bash
aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

### Step 2: Deploy Lambda Functions

Package and deploy Lambda functions:

```bash
# Package Lambda functions
cd backend/lambda
zip -r training_handler.zip training_handler.py
zip -r inference_handler.zip inference_handler.py
zip -r model_registry_handler.zip model_registry_handler.py

# Update Lambda functions
aws lambda update-function-code \
  --function-name mlops-platform-training-handler-dev \
  --zip-file fileb://training_handler.zip

aws lambda update-function-code \
  --function-name mlops-platform-inference-handler-dev \
  --zip-file fileb://inference_handler.zip

aws lambda update-function-code \
  --function-name mlops-platform-model-registry-handler-dev \
  --zip-file fileb://model_registry_handler.zip
```

### Step 3: Upload Dataset to S3

Upload the diabetic dataset:

```bash
# Get bucket name from CloudFormation output
DATA_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`DataBucketName`].OutputValue' \
  --output text)

# Upload dataset
aws s3 cp diabetic_data.csv s3://${DATA_BUCKET}/datasets/diabetic_data.csv
```

### Step 4: Build and Deploy Frontend

Build the React application:

```bash
cd frontend

# Install dependencies
npm install

# Set API endpoint
export REACT_APP_API_URL=<YOUR_API_ENDPOINT_FROM_STEP_1>

# Build for production
npm run build
```

Deploy to S3 (optional - for static hosting):

```bash
# Create S3 bucket for frontend
aws s3 mb s3://mlops-platform-frontend-dev

# Enable static website hosting
aws s3 website s3://mlops-platform-frontend-dev \
  --index-document index.html

# Upload build files
aws s3 sync build/ s3://mlops-platform-frontend-dev/ --acl public-read
```

Or deploy to CloudFront for production.

### Step 5: Test the Deployment

Test the API:

```bash
# Test training endpoint
curl -X POST ${API_ENDPOINT}/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "datasetUri": "s3://'${DATA_BUCKET}'/datasets/diabetic_data.csv",
    "modelName": "medication-adherence-model",
    "algorithm": "RandomForest",
    "instanceType": "ml.m5.xlarge"
  }'

# Test model registry
curl ${API_ENDPOINT}/models
```

## Configuration

### Environment Variables

The following environment variables are set automatically by CloudFormation:

- `SAGEMAKER_ROLE_ARN`: IAM role for SageMaker
- `MODEL_BUCKET`: S3 bucket for models
- `DATA_BUCKET`: S3 bucket for data
- `MODELS_TABLE`: DynamoDB table for model registry

### Frontend Configuration

Update `frontend/src/App.js` or create `.env` file:

```
REACT_APP_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

## Monitoring

### CloudWatch Logs

View Lambda logs:

```bash
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow
```

### SageMaker Training Jobs

List training jobs:

```bash
aws sagemaker list-training-jobs --max-results 10
```

Describe a training job:

```bash
aws sagemaker describe-training-job --training-job-name <job-name>
```

## Cost Optimization

1. **SageMaker**: Use spot instances for training
2. **Lambda**: Optimize memory and timeout settings
3. **S3**: Enable lifecycle policies for old data
4. **DynamoDB**: Use on-demand billing for variable workloads

## Cleanup

To delete all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name mlops-platform-dev

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name mlops-platform-dev

# Delete S3 buckets (if not empty)
aws s3 rm s3://${DATA_BUCKET} --recursive
aws s3 rb s3://${DATA_BUCKET}

aws s3 rm s3://${MODEL_BUCKET} --recursive
aws s3 rb s3://${MODEL_BUCKET}
```

## Troubleshooting

### Lambda Function Errors

Check CloudWatch Logs for detailed error messages:

```bash
aws logs tail /aws/lambda/<function-name> --follow
```

### SageMaker Training Failures

Check training job logs:

```bash
aws sagemaker describe-training-job --training-job-name <job-name>
```

### API Gateway Issues

Test API Gateway directly:

```bash
aws apigatewayv2 get-apis
```

## Security Best Practices

1. Enable encryption at rest for S3 buckets
2. Use VPC endpoints for SageMaker
3. Implement API Gateway authentication (Cognito or IAM)
4. Enable CloudTrail for audit logging
5. Use AWS Secrets Manager for sensitive configuration

## Next Steps

1. Set up CI/CD pipeline using AWS CodePipeline
2. Implement model monitoring with SageMaker Model Monitor
3. Add authentication using Amazon Cognito
4. Set up CloudWatch alarms for critical metrics
5. Implement automated model retraining triggers
