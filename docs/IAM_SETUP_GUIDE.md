# IAM Permissions Setup Guide

This guide explains how to set up the required IAM permissions for deploying the MLOps Platform.

## Overview

The deployment requires various AWS permissions to create and manage resources including:
- CloudFormation stacks
- S3 buckets
- Lambda functions
- DynamoDB tables
- API Gateway
- SageMaker resources
- CI/CD pipeline components (CodeCommit, CodeBuild, CodePipeline)
- Data pipeline components (Glue, Step Functions, EventBridge)

## Quick Setup (Automated)

Run the automated setup script:

```bash
chmod +x setup-iam-permissions.sh
./setup-iam-permissions.sh
```

This script will:
1. Create an IAM policy with all required permissions
2. Attach the policy to your current IAM user or role
3. Verify the permissions are working

## Manual Setup

If you prefer to set up permissions manually or need to customize them:

### Option 1: Attach AWS Managed Policies (Easiest)

Attach these AWS managed policies to your IAM user/role:

```bash
# Get your username
USERNAME=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)

# Attach managed policies
aws iam attach-user-policy --user-name $USERNAME --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
aws iam attach-user-policy --user-name $USERNAME --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
```

**Note**: These are broad permissions. For production, use the custom policy below.

### Option 2: Create Custom Policy (Recommended for Production)

1. Create the policy from the provided JSON file:

```bash
aws iam create-policy \
  --policy-name MLOpsPlatformDeploymentPolicy \
  --policy-document file://infrastructure/deployment-iam-policy.json \
  --description "Deployment permissions for MLOps Platform"
```

2. Get the policy ARN (replace ACCOUNT_ID with your AWS account ID):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/MLOpsPlatformDeploymentPolicy"
```

3. Attach to your IAM user:

```bash
USERNAME=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)
aws iam attach-user-policy --user-name $USERNAME --policy-arn $POLICY_ARN
```

4. Or attach to an IAM role:

```bash
ROLE_NAME="your-role-name"
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn $POLICY_ARN
```

## Required Permissions Summary

The deployment requires permissions for:

### Core Infrastructure
- **CloudFormation**: Create/update/delete stacks
- **S3**: Create buckets, upload/download objects
- **IAM**: Create roles and policies for services
- **CloudWatch Logs**: Create log groups and streams

### Compute & ML
- **Lambda**: Create and update functions
- **SageMaker**: Create training jobs, models, and endpoints
- **API Gateway**: Create REST APIs and deployments

### Data Storage
- **DynamoDB**: Create tables for model registry
- **S3**: Store datasets and models

### CI/CD Pipeline
- **CodeCommit**: Create repositories
- **CodeBuild**: Create build projects
- **CodePipeline**: Create deployment pipelines

### Data Pipeline
- **Glue**: Create ETL jobs and crawlers
- **Step Functions**: Create state machines
- **EventBridge**: Create rules for automation

### Frontend Hosting
- **Amplify**: Create and deploy web applications

## Verification

After setting up permissions, verify they work:

```bash
# Run prerequisites check
./prereq.sh

# Should show:
# ✓ CloudFormation accessible
# ✓ SageMaker accessible
# ✓ S3 accessible
# ✓ Lambda accessible
```

## Troubleshooting

### Permission Denied Errors

If you see permission errors during deployment:

1. **Wait for propagation**: IAM changes can take 10-30 seconds to propagate
2. **Check policy attachment**:
   ```bash
   aws iam list-attached-user-policies --user-name YOUR_USERNAME
   ```
3. **Check specific permission**: Look at the error message for the specific action denied
4. **Review CloudWatch logs**: Check for detailed error messages

### Common Issues

**Issue**: `CloudFormation not accessible`
- **Solution**: Ensure `cloudformation:*` permissions are attached

**Issue**: `Access Denied when creating S3 bucket`
- **Solution**: Verify S3 permissions and bucket naming (must be globally unique)

**Issue**: `Cannot pass role to Lambda/SageMaker`
- **Solution**: Ensure you have `iam:PassRole` permission

### Minimum Permissions for Testing

If you want to test with minimal permissions, you need at least:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "lambda:*",
        "iam:*",
        "dynamodb:*",
        "apigateway:*",
        "logs:*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## Security Best Practices

1. **Use least privilege**: Only grant permissions needed for your use case
2. **Use roles for EC2**: If deploying from EC2, use instance roles instead of access keys
3. **Rotate credentials**: Regularly rotate IAM access keys
4. **Enable MFA**: Enable multi-factor authentication for IAM users
5. **Use separate accounts**: Consider separate AWS accounts for dev/staging/prod
6. **Tag resources**: Use tags to track resources created by the deployment

## For AWS Organizations

If you're using AWS Organizations:

1. Ensure Service Control Policies (SCPs) allow the required actions
2. Consider using a dedicated deployment account
3. Use cross-account roles for accessing resources in other accounts

## Next Steps

After setting up IAM permissions:

1. Run `./prereq.sh` to verify all prerequisites
2. Run `./deploy-complete.sh` to deploy the platform
3. Review `DEPLOYMENT_INFO.txt` for deployment details

## Support

If you encounter permission issues:

1. Check the error message for the specific permission denied
2. Review the IAM policy in `infrastructure/deployment-iam-policy.json`
3. Consult AWS documentation for the specific service
4. Check CloudTrail logs for detailed API call information

## References

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS CloudFormation Permissions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html)
- [AWS SageMaker Permissions](https://docs.aws.amazon.com/sagemaker/latest/dg/security-iam.html)
