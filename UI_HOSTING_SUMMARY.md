# UI Hosting - AWS Amplify

## ✅ Changed from CloudFront to AWS Amplify

### Why Amplify is Better

| Feature | CloudFront + S3 | AWS Amplify |
|---------|----------------|-------------|
| Setup | Complex (3 services) | Simple (1 service) |
| Deployment | Manual upload | Git push = deploy |
| CI/CD | Need CodePipeline | Built-in |
| SSL | Manual | Automatic |
| Cost | $5-20/month | $2/month |
| Rollback | Manual | One-click |

**Amplify = CloudFront + S3 + CI/CD + SSL in one!**

---

## 🚀 How to Deploy UI

### Method 1: Amplify Console (Easiest - 5 minutes)

1. **Go to AWS Amplify Console**
   ```
   https://console.aws.amazon.com/amplify/
   ```

2. **Click "New app" → "Host web app"**

3. **Connect GitHub**
   - Select repository: `your-org/mlops-platform`
   - Select branch: `main`

4. **Amplify auto-detects React**
   - Build settings configured automatically

5. **Add environment variable**
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-api.amazonaws.com/prod`

6. **Click "Save and deploy"**

7. **Done!** Your UI is at:
   ```
   https://main.xxxxx.amplifyapp.com
   ```

### Method 2: CloudFormation (Automated)

```bash
# Get API endpoint first
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name mlops-platform-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Deploy frontend
aws cloudformation deploy \
  --template-file infrastructure/frontend-hosting.yaml \
  --stack-name mlops-frontend-dev \
  --parameter-overrides \
    GitHubRepo=your-org/mlops-platform \
    GitHubBranch=main \
    GitHubToken=<your-github-token> \
    ApiEndpoint=$API_ENDPOINT \
  --capabilities CAPABILITY_NAMED_IAM

# Get URL
aws cloudformation describe-stacks \
  --stack-name mlops-frontend-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AmplifyDefaultDomain`].OutputValue' \
  --output text
```

---

## 🔄 Automatic Deployments

**Every Git push automatically deploys!**

```
1. Edit React code
2. git push origin main
3. Amplify builds and deploys
4. UI updated in 2 minutes!
```

No manual steps needed!

---

## 💰 Cost

**AWS Amplify Pricing:**
- Build: $0.01/build minute
- Hosting: $0.15/GB served
- Storage: $0.023/GB/month

**Free Tier:**
- 1000 build minutes/month
- 15 GB served/month
- 5 GB storage

**Typical Cost: $0-2/month** (vs $5-20 for CloudFront)

---

## 📁 Files Created

```
infrastructure/
└── frontend-hosting.yaml        ✅ Amplify CloudFormation

Documentation:
└── AMPLIFY_DEPLOYMENT_GUIDE.md  ✅ Complete guide
```

---

## ✅ Benefits

✅ **Simpler** - One service instead of three
✅ **Faster** - Deploy in 2 minutes
✅ **Cheaper** - $2/month vs $5-20/month
✅ **Automatic CI/CD** - Git push = deploy
✅ **Free SSL** - HTTPS automatic
✅ **PR Previews** - Test before merge
✅ **One-Click Rollback** - Easy to undo

---

## 🚀 Quick Start

```bash
# 1. Deploy backend
./deploy-complete.sh

# 2. Deploy frontend via Amplify Console
# Go to: https://console.aws.amazon.com/amplify/
# Click: New app → Host web app
# Connect: GitHub → your-org/mlops-platform
# Add env: REACT_APP_API_URL = <your-api-endpoint>
# Deploy!

# 3. Access UI
# https://main.xxxxx.amplifyapp.com
```

---

## 📚 Documentation

- **AMPLIFY_DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **infrastructure/frontend-hosting.yaml** - CloudFormation template

---

**AWS Amplify = Simpler, Faster, Cheaper!** 🚀

No more CloudFront complexity - just Git push and deploy!
