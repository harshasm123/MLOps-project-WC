#!/bin/bash

# Quick IAM Setup - Attaches required permissions to current user
# For detailed setup, see docs/IAM_SETUP_GUIDE.md

set -e

echo "========================================="
echo "Quick IAM Permissions Setup"
echo "========================================="
echo ""

# Get current user info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
USERNAME=$(echo $USER_ARN | cut -d'/' -f2)

echo "Setting up permissions for:"
echo "  User: $USERNAME"
echo "  Account: $ACCOUNT_ID"
echo ""

# Create policy
POLICY_NAME="MLOpsPlatformDeploymentPolicy"
echo "Creating IAM policy: $POLICY_NAME"

POLICY_ARN=$(aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://infrastructure/deployment-iam-policy.json \
    --description "MLOps Platform deployment permissions" \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || \
    echo "arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}")

echo "Policy ARN: $POLICY_ARN"
echo ""

# Attach policy
echo "Attaching policy to user: $USERNAME"
aws iam attach-user-policy \
    --user-name $USERNAME \
    --policy-arn $POLICY_ARN 2>/dev/null || echo "Policy already attached"

echo ""
echo "✓ Setup complete!"
echo ""
echo "Waiting 10 seconds for permissions to propagate..."
sleep 10

echo ""
echo "Testing CloudFormation access..."
if aws cloudformation list-stacks --max-results 1 >/dev/null 2>&1; then
    echo "✓ CloudFormation access verified!"
else
    echo "⚠ CloudFormation access failed. Wait a bit longer and try again."
fi

echo ""
echo "You can now run: ./deploy-complete.sh"
echo ""
