# GitOps Guide for MLOps Platform

This guide explains how to use **GitOps** with **GitHub** for the MLOps Platform (CodeCommit is deprecated).

## 🎯 GitOps Principles

1. **Git as Single Source of Truth** - All configuration in Git
2. **Declarative Configuration** - Infrastructure as Code
3. **Automated Deployment** - CI/CD via GitHub Actions
4. **Continuous Reconciliation** - Auto-sync with desired state

---

## 🏗️ Architecture

```
GitHub Repository (Source of Truth)
        ↓
GitHub Actions (CI/CD)
        ↓
    ┌───────────────────────┐
    │  Build & Test         │
    │  - Unit tests         │
    │  - Property tests     │
    │  - Lint code          │
    └───────────────────────┘
        ↓
    ┌───────────────────────┐
    │  Package              │
    │  - Lambda functions   │
    │  - Glue scripts       │
    └───────────────────────┘
        ↓
    ┌───────────────────────┐
    │  Deploy to AWS        │
    │  - Update Lambda      │
    │  - Upload to S3       │
    │  - Update Glue        │
    └───────────────────────┘
        ↓
    ┌───────────────────────┐
    │  Integration Tests    │
    │  - API health check   │
    │  - End-to-end tests   │
    └───────────────────────┘
```

---

## 📋 Prerequisites

### 1. GitHub Repository Setup

```bash
# Create a new repository on GitHub
# Then clone it locally
git clone https://github.com/your-org/mlops-platform.git
cd mlops-platform

# Copy all project files to the repository
cp -r /path/to/Weather\ Company\ Project/* .

# Commit and push
git add .
git commit -m "Initial commit: MLOps Platform"
git push origin main
```

### 2. GitHub Secrets Configuration

Go to **Settings → Secrets and variables → Actions** and add:

```
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_REGION=us-east-1
```

### 3. GitHub Token (for CloudFormation)

Create a Personal Access Token:
1. Go to **Settings → Developer settings → Personal access tokens**
2. Generate new token (classic)
3. Select scopes: `repo`, `admin:repo_hook`
4. Copy the token

---

## 🚀 Deployment Methods

### Method 1: Automated Deployment (GitOps)

**Every push to `main` branch automatically deploys:**

```bash
# Make changes
git add .
git commit -m "Update Lambda function"
git push origin main

# GitHub Actions will:
# 1. Run tests
# 2. Build packages
# 3. Deploy to AWS
# 4. Run integration tests
```

### Method 2: Manual Deployment via GitHub Actions

1. Go to **Actions** tab in GitHub
2. Select **Deploy Infrastructure** workflow
3. Click **Run workflow**
4. Choose environment (dev/staging/prod)
5. Click **Run workflow**

### Method 3: Local Deployment with GitHub

```bash
# Deploy infrastructure
aws cloudformation deploy \
  --template-file infrastructure/cloudformation-template.yaml \
  --stack-name mlops-platform-dev \
  --parameter-overrides \
    Environment=dev \
  --capabilities CAPABILITY_NAMED_IAM

# Deploy CI/CD pipeline with GitHub
aws cloudformation deploy \
  --template-file infrastructure/cicd-pipeline.yaml \
  --stack-name mlops-cicd-dev \
  --parameter-overrides \
    Environment=dev \
    GitHubRepo=your-org/mlops-platform \
    GitHubBranch=main \
    GitHubToken=<your-github-token> \
  --capabilities CAPABILITY_NAMED_IAM
```

---

## 📁 Repository Structure

```
mlops-platform/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml                    # Main CI/CD pipeline
│       └── deploy-infrastructure.yml    # Infrastructure deployment
├── infrastructure/
│   ├── cloudformation-template.yaml     # Main infrastructure
│   ├── cicd-pipeline.yaml              # CI/CD with GitHub
│   ├── data-pipeline.yaml              # Data pipeline
│   └── gitops-config.yaml              # GitOps configuration
├── backend/lambda/                      # Lambda functions
├── glue-scripts/                        # Glue ETL scripts
├── frontend/                            # React UI
├── src/                                 # Python ML code
├── tests/                               # Test suite
└── README.md
```

---

## 🔄 GitOps Workflows

### Workflow 1: CI/CD Pipeline

**Trigger**: Push to `main` or `develop`, or Pull Request

**Steps**:
1. **Build & Test**
   - Install dependencies
   - Run unit tests
   - Run property-based tests
   - Generate coverage report
   - Lint code

2. **Build Lambda**
   - Package Lambda functions
   - Upload artifacts

3. **Deploy** (main branch only)
   - Configure AWS credentials
   - Update Lambda functions
   - Upload Glue scripts
   - Notify success

4. **Integration Test**
   - Test API endpoints
   - Verify deployment

**File**: `.github/workflows/ci-cd.yml`

### Workflow 2: Infrastructure Deployment

**Trigger**: 
- Push to `main` with changes in `infrastructure/`
- Manual workflow dispatch

**Steps**:
1. Validate CloudFormation templates
2. Deploy main infrastructure
3. Deploy CI/CD pipeline
4. Deploy data pipeline
5. Output stack information

**File**: `.github/workflows/deploy-infrastructure.yml`

---

## 🔐 Security Best Practices

### 1. GitHub Secrets
- Store AWS credentials in GitHub Secrets
- Never commit credentials to repository
- Rotate secrets regularly

### 2. Branch Protection
Enable branch protection for `main`:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date

### 3. Least Privilege IAM
Create dedicated IAM user for GitHub Actions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "s3:PutObject",
        "cloudformation:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🧪 Testing Strategy

### Local Testing

```bash
# Run tests locally before pushing
pytest tests/ -v --cov=src

# Run property-based tests
pytest tests/ -m property -v

# Lint code
flake8 src/ backend/ --max-line-length=120
```

### CI Testing

GitHub Actions automatically runs:
- Unit tests
- Property-based tests
- Integration tests
- Code coverage analysis

### Manual Testing

```bash
# Test API after deployment
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

curl $API_ENDPOINT/models
```

---

## 🔄 Deployment Strategies

### Blue-Green Deployment

```yaml
# In gitops-config.yaml
deployment:
  strategy: blue-green
  approval_required: true
```

**Process**:
1. Deploy new version (green)
2. Run tests on green
3. Switch traffic to green
4. Keep blue for rollback

### Canary Deployment

```yaml
deployment:
  strategy: canary
  canary_percentage: 10
  canary_duration: 30m
```

**Process**:
1. Deploy to 10% of traffic
2. Monitor for 30 minutes
3. Gradually increase to 100%
4. Rollback if errors detected

---

## 📊 Monitoring GitOps

### GitHub Actions Monitoring

View workflow runs:
1. Go to **Actions** tab
2. See all workflow runs
3. Click on run for details
4. View logs for each step

### AWS Monitoring

```bash
# View Lambda logs
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow

# View CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name mlops-platform-dev \
  --max-items 10
```

### Metrics Dashboard

Create CloudWatch dashboard:
- Deployment frequency
- Deployment success rate
- Mean time to recovery
- Change failure rate

---

## 🐛 Troubleshooting

### Deployment Fails

```bash
# Check GitHub Actions logs
# Go to Actions tab → Failed workflow → View logs

# Check CloudFormation
aws cloudformation describe-stack-events \
  --stack-name mlops-platform-dev

# Check Lambda function
aws lambda get-function \
  --function-name mlops-platform-training-handler-dev
```

### Tests Fail

```bash
# Run tests locally
pytest tests/ -v

# Check specific test
pytest tests/test_config_properties.py -v

# View coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### GitHub Webhook Issues

```bash
# Verify webhook in CloudFormation
aws cloudformation describe-stacks \
  --stack-name mlops-cicd-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue'

# Check webhook in GitHub
# Go to Settings → Webhooks → View recent deliveries
```

---

## 🔄 Rollback Procedures

### Rollback Lambda Function

```bash
# List versions
aws lambda list-versions-by-function \
  --function-name mlops-platform-training-handler-dev

# Rollback to previous version
aws lambda update-function-code \
  --function-name mlops-platform-training-handler-dev \
  --s3-bucket <bucket> \
  --s3-key <previous-version-key>
```

### Rollback Infrastructure

```bash
# Revert Git commit
git revert HEAD
git push origin main

# Or rollback CloudFormation
aws cloudformation update-stack \
  --stack-name mlops-platform-dev \
  --use-previous-template
```

---

## 📚 Additional Resources

### GitHub Actions Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [AWS Actions](https://github.com/aws-actions)

### GitOps Resources
- [GitOps Principles](https://www.gitops.tech/)
- [ArgoCD](https://argo-cd.readthedocs.io/)
- [Flux](https://fluxcd.io/)

### AWS Resources
- [AWS CloudFormation](https://docs.aws.amazon.com/cloudformation/)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon SageMaker](https://docs.aws.amazon.com/sagemaker/)

---

## ✅ Checklist

Before going to production:

- [ ] GitHub repository created
- [ ] GitHub Secrets configured
- [ ] Branch protection enabled
- [ ] CI/CD workflow tested
- [ ] Infrastructure deployed
- [ ] Integration tests passing
- [ ] Monitoring configured
- [ ] Rollback procedure tested
- [ ] Documentation updated
- [ ] Team trained on GitOps

---

## 🎉 Summary

**GitOps Benefits**:
- ✅ Git as single source of truth
- ✅ Automated deployments
- ✅ Easy rollbacks
- ✅ Audit trail in Git history
- ✅ Collaboration via Pull Requests
- ✅ No CodeCommit dependency

**Next Steps**:
1. Set up GitHub repository
2. Configure GitHub Secrets
3. Push code to GitHub
4. Watch automated deployment
5. Monitor in CloudWatch

**Your MLOps platform is now fully GitOps-enabled!** 🚀
