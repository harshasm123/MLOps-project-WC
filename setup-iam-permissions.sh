#!/bin/bash

# IAM Permissions Setup Script
# This script creates an IAM policy and attaches it to your user or role

set -e

echo "========================================="
echo "MLOps Platform - IAM Permissions Setup"
echo "========================================="
echo ""

# Get current IAM identity
IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $IDENTITY | jq -r '.Account')
USER_ARN=$(echo $IDENTITY | jq -r '.Arn')
USER_TYPE=$(echo $USER_ARN | cut -d':' -f6 | cut -d'/' -f1)

echo "Current Identity:"
echo "  Account: $ACCOUNT_ID"
echo "  ARN: $USER_ARN"
echo "  Type: $USER_TYPE"
echo ""

# Policy configuration
POLICY_NAME="MLOpsPlatformDeploymentPolicy"
POLICY_FILE="infrastructure/deployment-iam-policy.json"

# Check if policy file exists
if [ ! -f "$POLICY_FILE" ]; then
    echo "Error: Policy file not found at $POLICY_FILE"
    exit 1
fi

echo "Step 1: Creating IAM policy..."

# Check if policy already exists
EXISTING_POLICY=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text)

if [ -z "$EXISTING_POLICY" ]; then
    # Create new policy
    POLICY_ARN=$(aws iam create-policy \
        --policy-name $POLICY_NAME \
        --policy-document file://$POLICY_FILE \
        --description "Deployment permissions for MLOps Platform" \
        --query 'Policy.Arn' \
        --output text)
    
    echo "✓ Policy created: $POLICY_ARN"
else
    POLICY_ARN=$EXISTING_POLICY
    echo "✓ Policy already exists: $POLICY_ARN"
    
    # Update policy with new version
    echo "  Updating policy to latest version..."
    aws iam create-policy-version \
        --policy-arn $POLICY_ARN \
        --policy-document file://$POLICY_FILE \
        --set-as-default > /dev/null
    echo "✓ Policy updated to latest version"
fi

echo ""
echo "Step 2: Attaching policy to your identity..."

if [ "$USER_TYPE" = "user" ]; then
    # Extract username from ARN
    USERNAME=$(echo $USER_ARN | cut -d'/' -f2)
    
    # Attach policy to user
    aws iam attach-user-policy \
        --user-name $USERNAME \
        --policy-arn $POLICY_ARN 2>/dev/null || echo "  Policy may already be attached"
    
    echo "✓ Policy attached to user: $USERNAME"
    
elif [ "$USER_TYPE" = "assumed-role" ]; then
    # Extract role name from ARN
    ROLE_NAME=$(echo $USER_ARN | cut -d'/' -f2)
    
    echo "⚠ You are using an assumed role: $ROLE_NAME"
    echo ""
    echo "To attach the policy to the role, run:"
    echo "  aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn $POLICY_ARN"
    echo ""
    echo "Or ask your administrator to attach the policy."
    
else
    echo "⚠ Unknown identity type. Please attach the policy manually:"
    echo "  Policy ARN: $POLICY_ARN"
fi

echo ""
echo "Step 3: Verifying permissions..."

# Test CloudFormation access
if aws cloudformation list-stacks --max-results 1 >/dev/null 2>&1; then
    echo "✓ CloudFormation access verified"
else
    echo "✗ CloudFormation access failed"
    echo "  Note: It may take a few seconds for permissions to propagate"
fi

echo ""
echo "========================================="
echo "IAM Setup Complete!"
echo "========================================="
echo ""
echo "Policy ARN: $POLICY_ARN"
echo ""
echo "Next Steps:"
echo "1. Wait 10-30 seconds for permissions to propagate"
echo "2. Run: ./prereq.sh (to verify all permissions)"
echo "3. Run: ./deploy-complete.sh (to deploy the platform)"
echo ""
echo "If you still see permission errors:"
echo "- Wait a bit longer for AWS IAM to propagate changes"
echo "- Verify the policy is attached: aws iam list-attached-user-policies --user-name $USERNAME"
echo "- Check CloudWatch logs for specific permission denials"
echo ""
echo "========================================="
