#!/bin/bash

# MLOps Platform IAM Setup Script
# Creates IAM policy and attaches to current user

set -euo pipefail

echo "=========================================="
echo "MLOps Platform IAM Setup"
echo "=========================================="

# Get current AWS user
CURRENT_USER=$(aws iam get-user --query 'User.UserName' --output text 2>/dev/null || echo "")

if [ -z "$CURRENT_USER" ]; then
  echo "Error: Unable to get current AWS user"
  echo "Ensure AWS credentials are configured: aws configure"
  exit 1
fi

echo "Current IAM User: $CURRENT_USER"

# Create IAM policy document
POLICY_NAME="MLOpsPlatformPolicy"
POLICY_FILE="/tmp/mlops-policy.json"

cat > "$POLICY_FILE" << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudFormation",
      "Effect": "Allow",
      "Action": [
        "cloudformation:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Lambda",
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "apigateway:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3",
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDB",
      "Effect": "Allow",
      "Action": [
        "dynamodb:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SageMaker",
      "Effect": "Allow",
      "Action": [
        "sagemaker:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAM",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "iam:GetRole",
        "iam:ListRolePolicies",
        "iam:GetRolePolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatch",
      "Effect": "Allow",
      "Action": [
        "logs:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Glue",
      "Effect": "Allow",
      "Action": [
        "glue:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "StepFunctions",
      "Effect": "Allow",
      "Action": [
        "states:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EventBridge",
      "Effect": "Allow",
      "Action": [
        "events:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudFront",
      "Effect": "Allow",
      "Action": [
        "cloudfront:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECR",
      "Effect": "Allow",
      "Action": [
        "ecr:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

echo "Step 1: Creating IAM policy..."

# Check if policy already exists
POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text 2>/dev/null || echo "")

if [ -z "$POLICY_ARN" ]; then
  echo "Creating new policy: $POLICY_NAME"
  POLICY_ARN=$(aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file://"$POLICY_FILE" \
    --query 'Policy.Arn' \
    --output text)
  echo "✓ Policy created: $POLICY_ARN"
else
  echo "✓ Policy already exists: $POLICY_ARN"
fi

echo ""
echo "Step 2: Attaching policy to user: $CURRENT_USER"

# Attach policy to user
aws iam attach-user-policy \
  --user-name "$CURRENT_USER" \
  --policy-arn "$POLICY_ARN"

echo "✓ Policy attached to user"

echo ""
echo "Step 3: Verifying permissions..."

# List attached policies
ATTACHED=$(aws iam list-attached-user-policies \
  --user-name "$CURRENT_USER" \
  --query "AttachedPolicies[?PolicyName=='$POLICY_NAME'].PolicyName" \
  --output text)

if [ -n "$ATTACHED" ]; then
  echo "✓ Policy successfully attached"
else
  echo "✗ Policy attachment verification failed"
  exit 1
fi

# Cleanup
rm -f "$POLICY_FILE"

echo ""
echo "=========================================="
echo "IAM Setup Complete!"
echo "=========================================="
echo ""
echo "User: $CURRENT_USER"
echo "Policy: $POLICY_NAME"
echo "ARN: $POLICY_ARN"
echo ""
echo "You can now deploy the MLOps Platform:"
echo "  ./deploy.sh --full-cloudfront"
echo ""
echo "=========================================="