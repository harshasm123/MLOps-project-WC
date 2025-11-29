# Quick Start Guide

Get the MLOps Platform running on AWS in under 10 minutes.

## Prerequisites Check

```bash
# Check AWS CLI
aws --version

# Check Node.js
node --version

# Check Python
python --version

# Verify AWS credentials
aws sts get-caller-identity
```

## Step 1: Clone and Setup (1 min)

```bash
# Navigate to project directory
cd "Weather Company Project"

# Make deployment script executable
chmod +x deploy.sh
```

## Step 2: Deploy to AWS (5-7 mins)

```bash
# Run automated deployment
./deploy.sh
```

This will:
- ✅ Create CloudFormation stack
- ✅ Deploy Lambda functions
- ✅ Set up API Gateway
- ✅ Create S3 buckets and DynamoDB table
- ✅ Upload dataset
- ✅ Build React frontend

## Step 3: Get Your API Endpoint

After deployment completes, note the API endpoint:

```
API Endpoint: https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod
```

## Step 4: Test the API (1 min)

```bash
# Set your API endpoint
export API_ENDPOINT="<your-api-endpoint-from-step-3>"

# Test model registry
curl $API_ENDPOINT/models

# Start a training job
curl -X POST $API_ENDPOINT/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "datasetUri": "s3://mlops-platform-data-dev-<account-id>/datasets/diabetic_data.csv",
    "modelName": "medication-adherence-model",
    "algorithm": "RandomForest",
    "instanceType": "ml.m5.xlarge"
  }'
```

## Step 5: Access the UI (1 min)

### Option A: Local Access

```bash
# Open in browser
open frontend/build/index.html
```

### Option B: Deploy to S3

```bash
# Create frontend bucket
aws s3 mb s3://mlops-platform-frontend-dev

# Enable static hosting
aws s3 website s3://mlops-platform-frontend-dev \
  --index-document index.html

# Upload files
aws s3 sync frontend/build/ s3://mlops-platform-frontend-dev/ --acl public-read

# Get URL
echo "http://mlops-platform-frontend-dev.s3-website-us-east-1.amazonaws.com"
```

## What You Can Do Now

### 1. Train a Model

Go to **Training Pipeline** tab:
- Dataset URI: `s3://your-data-bucket/datasets/diabetic_data.csv`
- Model Name: `medication-adherence-model`
- Algorithm: `RandomForest`
- Click **Start Training**

### 2. Run Predictions

Go to **Inference Pipeline** tab:
- Input Data URI: `s3://your-data-bucket/inference_data.csv`
- Model Version: `latest`
- Click **Run Inference**

### 3. View Models

Go to **Models** tab to see:
- All trained models
- Performance metrics
- Approval status
- Approve models for deployment

### 4. Monitor Performance

Go to **Monitoring** tab to see:
- Data drift over time
- Active alerts
- Model performance metrics

## Troubleshooting

### Deployment Failed

```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name mlops-platform-dev \
  --max-items 10

# Check stack status
aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev
```

### Lambda Errors

```bash
# View logs
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow
```

### Training Job Failed

```bash
# List recent jobs
aws sagemaker list-training-jobs --max-results 5

# Get job details
aws sagemaker describe-training-job --training-job-name <job-name>
```

## Next Steps

1. **Upload Your Own Data**: Replace `diabetic_data.csv` with your dataset
2. **Customize Models**: Modify hyperparameters in the UI
3. **Set Up Monitoring**: Configure CloudWatch alarms
4. **Add Authentication**: Integrate AWS Cognito
5. **Enable CI/CD**: Set up CodePipeline for automated deployments

## Clean Up

When you're done testing:

```bash
# Delete everything
aws cloudformation delete-stack --stack-name mlops-platform-dev

# Verify deletion
aws cloudformation wait stack-delete-complete --stack-name mlops-platform-dev
```

## Cost Estimate

Running this platform costs approximately:
- **Lambda**: $0.20/day (minimal usage)
- **API Gateway**: $3.50/million requests
- **SageMaker Training**: $0.269/hour (ml.m5.xlarge)
- **S3**: $0.023/GB/month
- **DynamoDB**: $0.25/GB/month (on-demand)

**Estimated monthly cost**: $10-50 depending on usage

## Support

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Review [README.md](README.md) for architecture details
- See specs in `.kiro/specs/mlops-platform/` for requirements

## Success Checklist

- [ ] CloudFormation stack created
- [ ] Lambda functions deployed
- [ ] API endpoint accessible
- [ ] Dataset uploaded to S3
- [ ] Frontend built successfully
- [ ] Can access UI
- [ ] Can start training jobs
- [ ] Can run inference
- [ ] Can view models in registry

🎉 **Congratulations!** Your MLOps platform is now running on AWS!
