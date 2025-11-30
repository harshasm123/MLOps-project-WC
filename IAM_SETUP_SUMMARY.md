# IAM Setup Summary

## What Was Added

I've added comprehensive IAM permission management to ensure your deployment runs smoothly.

## New Files Created

### 1. `infrastructure/deployment-iam-policy.json`
A complete IAM policy document with all required permissions for deploying the MLOps platform, including:
- CloudFormation (create/update/delete stacks)
- S3 (bucket management and object operations)
- Lambda (function creation and updates)
- IAM (role and policy management)
- DynamoDB (table operations)
- API Gateway (REST API management)
- SageMaker (ML operations)
- CodeCommit, CodeBuild, CodePipeline (CI/CD)
- Glue, Step Functions, EventBridge (data pipeline)
- CloudWatch Logs (monitoring)
- Amplify (frontend hosting)

### 2. `setup-iam-quick.sh`
Quick setup script that:
- Creates the IAM policy from the JSON file
- Attaches it to your current IAM user
- Verifies CloudFormation access
- Takes ~10 seconds to complete

### 3. `setup-iam-permissions.sh`
Comprehensive setup script that:
- Detects your IAM identity (user or role)
- Creates or updates the IAM policy
- Attaches to user or provides instructions for roles
- Verifies all permissions
- Provides troubleshooting guidance

### 4. `docs/IAM_SETUP_GUIDE.md`
Complete documentation including:
- Quick setup instructions
- Manual setup options
- Permission requirements breakdown
- Troubleshooting guide
- Security best practices
- AWS Organizations guidance

### 5. Updated `README.md`
Added IAM setup as Step 1 in the deployment process.

## How to Use

### Option 1: Quick Setup (Recommended)

```bash
chmod +x setup-iam-quick.sh
./setup-iam-quick.sh
```

This will:
1. Create the IAM policy
2. Attach it to your user
3. Wait for propagation
4. Verify access

### Option 2: Comprehensive Setup

```bash
chmod +x setup-iam-permissions.sh
./setup-iam-permissions.sh
```

This provides more detailed output and handles both users and roles.

### Option 3: Manual Setup

If you prefer manual control or are using AWS Organizations:

1. Review the policy: `infrastructure/deployment-iam-policy.json`
2. Create it in IAM Console or via CLI
3. Attach to your user/role
4. Follow instructions in `docs/IAM_SETUP_GUIDE.md`

## Deployment Flow

Now your deployment process is:

```bash
# 1. Setup IAM permissions
./setup-iam-quick.sh

# 2. Verify prerequisites
./prereq.sh

# 3. Deploy the platform
./deploy-complete.sh
```

## What This Fixes

The original issue was:
```
⚠ CloudFormation not accessible (check IAM permissions)
```

And during deployment:
```
An error occurred (ValidationError) when calling the CreateStack operation
```

These scripts ensure you have all required permissions before attempting deployment.

## Security Notes

- The policy follows least-privilege principles for MLOps deployments
- All resources are scoped where possible (e.g., S3 buckets with `mlops-platform-*` prefix)
- For production, review and customize the policy based on your security requirements
- Consider using separate AWS accounts for dev/staging/prod environments

## Troubleshooting

If you still see permission errors after running the setup:

1. **Wait for propagation**: IAM changes can take 10-30 seconds
2. **Check attachment**: 
   ```bash
   aws iam list-attached-user-policies --user-name YOUR_USERNAME
   ```
3. **Review specific error**: The error message will tell you which permission is missing
4. **Check CloudTrail**: For detailed API call logs

## Next Steps

After setting up IAM permissions:

1. Run `./prereq.sh` - Should now show ✓ for CloudFormation
2. Run `./deploy-complete.sh` - Should deploy successfully
3. Check `DEPLOYMENT_INFO.txt` for deployment details

## Support

For detailed information, see:
- `docs/IAM_SETUP_GUIDE.md` - Complete IAM setup guide
- `docs/DEPLOYMENT.md` - Deployment instructions
- `docs/AWS_WELL_ARCHITECTED.md` - Architecture details
