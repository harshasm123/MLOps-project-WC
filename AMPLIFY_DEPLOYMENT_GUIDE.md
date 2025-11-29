# AWS Amplify Deployment Guide

## Why AWS Amplify Instead of CloudFront?

AWS Amplify is **simpler, faster, and better** for React apps:

| Feature | CloudFront + S3 | AWS Amplify |
|---------|----------------|-------------|
| **Setup** | Manual (S3 + CloudFront + Route53) | Automatic |
| **CI/CD** | Need CodePipeline | Built-in |
| **SSL** | Manual certificate | Automatic HTTPS |
| **Deployment** | Manual upload | Git push = deploy |
| **Preview** | No | PR previews |
| **Rollback** | Manual | One-click |
| **Cost** | $5-20/month | $0.01/build + $0.15/GB |

**Amplify = CloudFront + S3 + CI/CD + SSL in one service!**

---

## 🚀 Three Ways to Deploy Frontend

### Method 1: Amplify with CloudFormation (Automated)

```bash
# Deploy frontend hosting
aws cloudformation deploy \
  --template-file infrastructure/frontend-hosting.yaml \
  --stack-name mlops-frontend-dev \
  --parameter-overrides \
    GitHubRepo=your-org/mlops-platform \
    GitHubBranch=main \
    GitHubToken=<your-github-token> \
    ApiEndpoint=https://your-api.amazonaws.com/prod \
  --capabilities CAPABILITY_NAMED_IAM

# Get the URL
aws cloudformation describe-stacks \
  --stack-name mlops-frontend-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AmplifyDefaultDomain`].OutputValue' \
  --output text
```

**What happens:**
- Amplify connects to your GitHub repo
- Builds React app automatically
- Deploys to `https://main.xxxxx.amplifyapp.com`
- Every Git push triggers automatic rebuild

### Method 2: Amplify Console (Manual, Easiest)

1. **Go to AWS Amplify Console**
   ```
   https://console.aws.amazon.com/amplify/
   ```

2. **Click "New app" → "Host web app"**

3. **Connect GitHub**
   - Select your repository
   - Select branch (main)
   - Amplify auto-detects React

4. **Configure build settings**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: frontend/build
       files:
         - '**/*'
   ```

5. **Add environment variable**
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-api.amazonaws.com/prod`

6. **Click "Save and deploy"**

7. **Done!** Your app is at:
   ```
   https://main.xxxxx.amplifyapp.com
   ```

### Method 3: Amplify CLI (For Developers)

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Configure Amplify
amplify configure

# Initialize in your project
cd frontend
amplify init

# Add hosting
amplify add hosting
# Select: Hosting with Amplify Console
# Select: Manual deployment

# Publish
amplify publish

# Your app is live!
```

---

## 🔄 Automatic Deployments

### How It Works

```
1. You push code to GitHub
        ↓
2. Amplify detects the push
        ↓
3. Amplify builds React app
   - npm install
   - npm run build
        ↓
4. Amplify deploys to CDN
        ↓
5. Your app is updated!
   https://main.xxxxx.amplifyapp.com
```

**Every Git push = automatic deployment!**

### Branch Deployments

```
main branch    → https://main.xxxxx.amplifyapp.com
develop branch → https://develop.xxxxx.amplifyapp.com
feature branch → https://feature.xxxxx.amplifyapp.com
```

### Pull Request Previews

When you create a PR:
```
PR #123 → https://pr-123.xxxxx.amplifyapp.com
```

Test before merging!

---

## 🎯 Complete Setup Example

### Step 1: Push Code to GitHub

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin https://github.com/your-org/mlops-platform.git
git push -u origin main
```

### Step 2: Deploy Backend

```bash
# Deploy API and Lambda
./deploy-complete.sh

# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

echo "API Endpoint: $API_ENDPOINT"
```

### Step 3: Deploy Frontend with Amplify

**Option A: Via Console (Easiest)**

1. Go to https://console.aws.amazon.com/amplify/
2. Click "New app" → "Host web app"
3. Connect GitHub → Select repo
4. Add environment variable:
   - `REACT_APP_API_URL` = `$API_ENDPOINT`
5. Click "Save and deploy"

**Option B: Via CloudFormation**

```bash
aws cloudformation deploy \
  --template-file infrastructure/frontend-hosting.yaml \
  --stack-name mlops-frontend-dev \
  --parameter-overrides \
    GitHubRepo=your-org/mlops-platform \
    GitHubToken=<token> \
    ApiEndpoint=$API_ENDPOINT \
  --capabilities CAPABILITY_NAMED_IAM
```

### Step 4: Access Your App

```bash
# Get Amplify URL
aws amplify list-apps

# Or from CloudFormation
aws cloudformation describe-stacks \
  --stack-name mlops-frontend-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AmplifyDefaultDomain`].OutputValue' \
  --output text
```

Open in browser:
```
https://main.xxxxx.amplifyapp.com
```

---

## 🔧 Configuration

### Environment Variables

Set in Amplify Console or CloudFormation:

```yaml
Environment Variables:
  REACT_APP_API_URL: https://your-api.amazonaws.com/prod
  REACT_APP_AWS_REGION: us-east-1
  REACT_APP_DEBUG: false
```

### Build Settings

Amplify auto-detects React, but you can customize:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - echo "REACT_APP_API_URL=$API_ENDPOINT" > .env
        - npm run build
  artifacts:
    baseDirectory: frontend/build
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### Custom Domain (Optional)

1. **In Amplify Console:**
   - Go to your app
   - Click "Domain management"
   - Click "Add domain"
   - Enter your domain: `mlops.yourdomain.com`
   - Amplify configures SSL automatically

2. **Via CloudFormation:**
   ```yaml
   AmplifyDomain:
     Type: AWS::Amplify::Domain
     Properties:
       AppId: !GetAtt AmplifyApp.AppId
       DomainName: 'yourdomain.com'
       SubDomainSettings:
         - Prefix: 'mlops'
           BranchName: 'main'
   ```

---

## 📊 Monitoring

### View Builds

**In Console:**
1. Go to Amplify Console
2. Select your app
3. See all builds and deployments

**Via CLI:**
```bash
# List apps
aws amplify list-apps

# Get app details
aws amplify get-app --app-id <app-id>

# List branches
aws amplify list-branches --app-id <app-id>
```

### Build Logs

View in Amplify Console:
- Provision
- Build
- Deploy
- Verify

### Metrics

Amplify provides:
- Build duration
- Deploy duration
- Traffic metrics
- Error rates

---

## 💰 Cost Comparison

### CloudFront + S3
```
CloudFront: $0.085/GB + $0.01/10,000 requests
S3: $0.023/GB storage
Route53: $0.50/hosted zone
Certificate Manager: Free
Total: ~$5-20/month
```

### AWS Amplify
```
Build: $0.01/build minute
Hosting: $0.15/GB served
Storage: $0.023/GB/month

Example (1000 visitors/month):
- 10 builds × 5 min = $0.50
- 10 GB served = $1.50
- 1 GB storage = $0.02
Total: ~$2/month

Free Tier:
- 1000 build minutes/month
- 15 GB served/month
- 5 GB storage
```

**Amplify is cheaper for most use cases!**

---

## 🔄 Deployment Workflow

### Development Workflow

```bash
# 1. Make changes to React app
cd frontend
# Edit src/components/Dashboard.js

# 2. Test locally
npm start

# 3. Commit and push
git add .
git commit -m "Update dashboard"
git push origin main

# 4. Amplify automatically:
#    - Detects push
#    - Builds app
#    - Deploys to CDN
#    - Updates https://main.xxxxx.amplifyapp.com

# 5. Done! Changes are live in ~2 minutes
```

### Multi-Environment Setup

```yaml
Environments:
  dev:
    branch: develop
    url: https://develop.xxxxx.amplifyapp.com
    api: https://dev-api.amazonaws.com/prod
  
  staging:
    branch: staging
    url: https://staging.xxxxx.amplifyapp.com
    api: https://staging-api.amazonaws.com/prod
  
  prod:
    branch: main
    url: https://main.xxxxx.amplifyapp.com
    api: https://prod-api.amazonaws.com/prod
```

---

## 🐛 Troubleshooting

### Build Fails

**Check build logs:**
1. Go to Amplify Console
2. Click on failed build
3. View logs

**Common issues:**

**Issue: "npm install failed"**
```yaml
# Fix: Specify Node version
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - nvm use 18
        - cd frontend
        - npm ci
```

**Issue: "REACT_APP_API_URL not set"**
```yaml
# Fix: Add environment variable
Environment Variables:
  REACT_APP_API_URL: https://your-api.amazonaws.com/prod
```

### App Not Loading

**Check:**
1. Build succeeded?
2. Environment variables set?
3. API endpoint correct?
4. CORS configured on API Gateway?

### Slow Builds

**Optimize:**
```yaml
# Enable caching
cache:
  paths:
    - frontend/node_modules/**/*
```

---

## 🔐 Security

### HTTPS

- Amplify provides HTTPS automatically
- Free SSL certificate
- No configuration needed

### Access Control

**Password protect (optional):**
1. Go to Amplify Console
2. Click "Access control"
3. Enable password protection
4. Set username/password

**IP whitelist (optional):**
```yaml
# In Amplify Console
Access control → IP restrictions
Add allowed IP ranges
```

---

## 🚀 Advanced Features

### Redirects and Rewrites

```json
[
  {
    "source": "/api/<*>",
    "target": "https://your-api.amazonaws.com/prod/<*>",
    "status": "200",
    "condition": null
  },
  {
    "source": "/<*>",
    "target": "/index.html",
    "status": "404-200",
    "condition": null
  }
]
```

### Custom Headers

```json
{
  "headers": [
    {
      "pattern": "**/*",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        }
      ]
    }
  ]
}
```

### Performance Monitoring

Enable in Amplify Console:
- Real User Monitoring (RUM)
- Performance metrics
- Error tracking

---

## 📚 Comparison Summary

### Why Amplify > CloudFront?

✅ **Simpler** - One service vs three (S3 + CloudFront + Route53)
✅ **Faster** - Git push = deployed in 2 minutes
✅ **Cheaper** - $2/month vs $5-20/month
✅ **CI/CD Built-in** - No CodePipeline needed
✅ **SSL Automatic** - No certificate management
✅ **PR Previews** - Test before merging
✅ **Rollback** - One-click to previous version
✅ **Monitoring** - Built-in metrics and logs

### When to Use CloudFront?

- Need advanced caching rules
- Multi-origin setup
- Lambda@Edge functions
- Very high traffic (>100GB/month)

### When to Use Amplify?

- React/Vue/Angular apps ✅
- Need CI/CD ✅
- Want simplicity ✅
- Low to medium traffic ✅
- **Perfect for this MLOps platform!** ✅

---

## ✅ Quick Start

```bash
# 1. Deploy backend
./deploy-complete.sh

# 2. Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# 3. Deploy frontend with Amplify
aws cloudformation deploy \
  --template-file infrastructure/frontend-hosting.yaml \
  --stack-name mlops-frontend-dev \
  --parameter-overrides \
    GitHubRepo=your-org/mlops-platform \
    GitHubToken=<token> \
    ApiEndpoint=$API_ENDPOINT \
  --capabilities CAPABILITY_NAMED_IAM

# 4. Get URL
aws cloudformation describe-stacks \
  --stack-name mlops-frontend-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AmplifyDefaultDomain`].OutputValue' \
  --output text

# 5. Open in browser!
```

---

**AWS Amplify = Simpler, Faster, Cheaper than CloudFront!** 🚀
