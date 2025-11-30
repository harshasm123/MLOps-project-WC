# MLOps Platform - Medication Adherence Prediction

A cloud-native MLOps platform deployed on AWS for predicting medication non-adherence in diabetic patients. Built with React frontend, Python backend, and AWS SageMaker for ML operations.

## 🎯 Use Case

Predict whether a patient will stop taking their medication (non-adherence) for a specific brand within the next 30 days, enabling proactive healthcare interventions.

## 🏗️ Architecture

### Frontend
- **React 18** with Material-UI
- Hosted on **AWS Amplify** (simpler than CloudFront!)
- Automatic CI/CD from GitHub
- Real-time dashboard for monitoring ML operations

### Backend
- **AWS Lambda** functions (Python 3.11)
- **API Gateway** for REST endpoints
- **DynamoDB** for model registry
- **S3** for data and model storage

### ML Infrastructure
- **Amazon SageMaker** for training and inference
- **CloudWatch** for monitoring and drift detection
- Automated pipelines for training and batch inference

### Complete Pipeline Architecture

**1. Data Pipeline (Glue + Step Functions)**
- AWS Glue for ETL and data validation
- Step Functions for workflow orchestration
- EventBridge for automated triggers
- Automated data quality checks

**2. CI/CD Pipeline (GitOps with GitHub Actions)**
- GitHub for source control (GitOps)
- GitHub Actions for CI/CD
- Automated build, test, and deployment
- Property-based testing with Hypothesis

**3. ML Training Pipeline (SageMaker)**
- Automated training job orchestration
- Model evaluation and registration
- Baseline statistics creation
- Multi-algorithm support

**4. ML Inference Pipeline (SageMaker)**
- Batch prediction processing
- Real-time drift detection
- CloudWatch metrics publishing
- Automated alerting

## 📁 Project Structure

```
.
├── frontend/                    # React UI
│   ├── src/
│   │   ├── components/         # Dashboard, Training, Inference, etc.
│   │   └── App.js
│   └── package.json
├── backend/                     # Lambda functions
│   └── lambda/
│       ├── training_handler.py
│       ├── inference_handler.py
│       └── model_registry_handler.py
├── infrastructure/              # CloudFormation templates
│   └── cloudformation-template.yaml
├── src/                        # Python ML code
│   ├── models/                 # Data models
│   ├── pipelines/              # Training/inference pipelines
│   └── monitoring/             # Drift detection
└── diabetic_data.csv           # Training dataset
```

## 🚀 Quick Deployment

### Prerequisites Check

Run the prerequisites checker to verify all dependencies:

```bash
chmod +x prereq.sh
./prereq.sh
```

This will check for:
- AWS CLI and credentials
- Python 3.9+
- Node.js 18+
- Git
- Required AWS service permissions

### Complete Deployment (All Pipelines)

```bash
chmod +x deploy-complete.sh
./deploy-complete.sh
```

This deploys:
1. ✅ **Main Infrastructure** (Lambda, API Gateway, S3, DynamoDB)
2. ✅ **CI/CD Pipeline** (CodePipeline, CodeBuild, CodeCommit)
3. ✅ **Data Pipeline** (Glue, Step Functions, EventBridge)
4. ✅ **Lambda Functions** (Training, Inference, Registry)
5. ✅ **Frontend Build** (React production bundle)

### Quick Deployment (Infrastructure Only)

```bash
chmod +x deploy.sh
./deploy.sh
```

Deploys only the main infrastructure without CI/CD and data pipelines.

### Manual Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed step-by-step instructions.

## 🖥️ Using the Platform

### Access the UI

After deployment, open `frontend/build/index.html` in your browser or deploy to S3:

```bash
aws s3 sync frontend/build/ s3://your-frontend-bucket/ --acl public-read
```

### Features

1. **Dashboard**: View system stats, active jobs, and alerts
2. **Training Pipeline**: Start new training jobs with custom parameters
3. **Inference Pipeline**: Run batch predictions on patient data
4. **Model Registry**: View, compare, and approve model versions
5. **Dataset Management**: Upload and manage datasets
6. **Monitoring**: Track data drift and model performance

### API Endpoints

```bash
# Start training job
POST /training/start
{
  "datasetUri": "s3://bucket/diabetic_data.csv",
  "modelName": "medication-adherence-model",
  "algorithm": "RandomForest",
  "instanceType": "ml.m5.xlarge"
}

# Run inference
POST /inference/predict
{
  "inputDataUri": "s3://bucket/inference_data.csv",
  "modelVersion": "latest"
}

# List models
GET /models
```

## 📊 Model Details

### Algorithm Options
- Random Forest (default)
- XGBoost
- Logistic Regression

### Features
- Patient demographics (age, gender)
- Medication brand
- Prescription history
- Refill patterns
- Previous adherence behavior
- Comorbidities

### Metrics
- Accuracy
- Precision (minimize false positives)
- Recall (minimize false negatives - critical for patient safety)
- F1-Score
- AUC-ROC

## 🔍 Monitoring

### View Logs

```bash
# Training logs
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow

# Inference logs
aws logs tail /aws/lambda/mlops-platform-inference-handler-dev --follow
```

### SageMaker Jobs

```bash
# List training jobs
aws sagemaker list-training-jobs --max-results 10

# Describe specific job
aws sagemaker describe-training-job --training-job-name <job-name>
```

## 💰 Cost Optimization

- Use **spot instances** for SageMaker training
- Enable **S3 lifecycle policies** for old data
- Use **DynamoDB on-demand** billing
- Set appropriate **Lambda timeouts** and memory

## 🧹 Cleanup

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name mlops-platform-dev

# Delete S3 buckets
aws s3 rm s3://mlops-platform-data-dev-<account-id> --recursive
aws s3 rb s3://mlops-platform-data-dev-<account-id>
```

## 🔒 Security

- All S3 buckets have encryption at rest
- IAM roles follow least privilege principle
- API Gateway supports CORS for frontend
- CloudTrail enabled for audit logging

## 📚 Documentation

### Getting Started
- 🚀 [Project Summary](docs/PROJECT_SUMMARY.md) - **START HERE** - Complete overview
- 🛠️ [Setup Scripts Guide](docs/SETUP_SCRIPTS.md) - ec2-setup.sh vs prereq.sh
- ⚡ [Quick Start Guide](docs/QUICKSTART.md) - Get started in minutes
- 📦 [Deployment Guide](docs/DEPLOYMENT.md) - Detailed deployment instructions

### Backend & API
- 🔧 [Backend Enhancements](docs/BACKEND_ENHANCEMENTS.md) - Lambda handlers, API endpoints
- 🤖 [SageMaker Execution Guide](docs/SAGEMAKER_EXECUTION_GUIDE.md) - Running ML jobs
- 📖 [Quick Reference](docs/QUICK_REFERENCE.md) - Common commands

### Architecture & Design
- 🏗️ [Complete Architecture](docs/COMPLETE_ARCHITECTURE.md) - Full system architecture
- ✅ [AWS Well-Architected](docs/AWS_WELL_ARCHITECTED.md) - Best practices alignment
- 📋 [Requirements](.kiro/specs/mlops-platform/requirements.md) - Feature requirements
- 🎨 [Design](.kiro/specs/mlops-platform/design.md) - Technical design
- ✔️ [Tasks](.kiro/specs/mlops-platform/tasks.md) - Implementation plan

### UI Specification (New!)
- 📱 [UI Requirements](.kiro/specs/medication-adherence-ui/requirements.md) - 14 requirements, 70 criteria
- 🎨 [UI Design](.kiro/specs/medication-adherence-ui/design.md) - 63 correctness properties
- ✅ [UI Tasks](.kiro/specs/medication-adherence-ui/tasks.md) - 21 tasks, 90+ sub-tasks

### CI/CD & Deployment
- 🔄 [GitOps Guide](docs/GITOPS_GUIDE.md) - GitOps workflow with GitHub Actions
- 📊 [GitOps vs CodeCommit](docs/GITOPS_VS_CODECOMMIT.md) - Migration rationale
- ☁️ [Amplify Deployment Guide](docs/AMPLIFY_DEPLOYMENT_GUIDE.md) - AWS Amplify setup
- 🌐 [UI Hosting Summary](docs/UI_HOSTING_SUMMARY.md) - Frontend hosting options

### Summaries
- 📄 [Deployment Summary](docs/DEPLOYMENT_SUMMARY.md) - Deployment overview
- 📝 [Final Summary](docs/FINAL_SUMMARY.md) - Complete project overview

## 🤝 Contributing

This project follows spec-driven development. See the specs in `.kiro/specs/mlops-platform/` for requirements and design.

## 📄 License

MIT License
