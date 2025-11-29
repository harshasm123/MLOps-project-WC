"""
Property-based tests for configuration validation.
Feature: mlops-platform, Property 27: Template storage in source control
"""

import pytest
from hypothesis import given, strategies as st
import os
from config.aws_config import AWSConfig


# Feature: mlops-platform, Property 27: Template storage in source control
# Validates: Requirements 8.1
@pytest.mark.property
@given(
    region=st.sampled_from(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']),
    s3_bucket=st.text(min_size=3, max_size=63, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-')),
    role_arn=st.text(min_size=20, max_size=100)
)
def test_config_validation_property(region, s3_bucket, role_arn):
    """
    Property: For any valid AWS configuration parameters, creating an AWSConfig
    should succeed and the configuration should be retrievable.
    
    This validates that configuration can be stored and retrieved consistently,
    which is essential for template storage in source control.
    """
    # Create configuration with generated values
    config = AWSConfig(
        region=region,
        s3_bucket=s3_bucket,
        model_registry_bucket=f"{s3_bucket}-models",
        data_bucket=f"{s3_bucket}-data",
        sagemaker_role_arn=role_arn if role_arn else "arn:aws:iam::123456789012:role/SageMakerRole",
        cloudwatch_namespace="MLOps/Platform"
    )
    
    # Verify configuration is valid
    assert config.region == region
    assert config.s3_bucket == s3_bucket
    assert config.sagemaker_role_arn is not None
    
    # Verify validation works
    if config.sagemaker_role_arn:
        assert config.validate() is True


def test_config_from_env():
    """Test that configuration can be loaded from environment variables."""
    # Set environment variables
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['MLOPS_S3_BUCKET'] = 'test-bucket'
    os.environ['MODEL_REGISTRY_BUCKET'] = 'test-model-bucket'
    os.environ['DATA_BUCKET'] = 'test-data-bucket'
    os.environ['SAGEMAKER_ROLE_ARN'] = 'arn:aws:iam::123456789012:role/TestRole'
    os.environ['CLOUDWATCH_NAMESPACE'] = 'Test/Namespace'
    
    # Load configuration
    config = AWSConfig.from_env()
    
    # Verify values
    assert config.region == 'us-east-1'
    assert config.s3_bucket == 'test-bucket'
    assert config.model_registry_bucket == 'test-model-bucket'
    assert config.data_bucket == 'test-data-bucket'
    assert config.sagemaker_role_arn == 'arn:aws:iam::123456789012:role/TestRole'
    assert config.cloudwatch_namespace == 'Test/Namespace'


def test_config_validation_fails_without_role():
    """Test that validation fails when required fields are missing."""
    config = AWSConfig(
        region='us-east-1',
        s3_bucket='test-bucket',
        model_registry_bucket='test-model-bucket',
        data_bucket='test-data-bucket',
        sagemaker_role_arn='',  # Empty role ARN
        cloudwatch_namespace='Test/Namespace'
    )
    
    with pytest.raises(ValueError, match="SAGEMAKER_ROLE_ARN must be set"):
        config.validate()


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    # Clear environment variables
    for key in ['AWS_REGION', 'MLOPS_S3_BUCKET', 'MODEL_REGISTRY_BUCKET', 
                'DATA_BUCKET', 'SAGEMAKER_ROLE_ARN', 'CLOUDWATCH_NAMESPACE']:
        os.environ.pop(key, None)
    
    config = AWSConfig.from_env()
    
    # Verify defaults
    assert config.region == 'us-east-1'
    assert config.s3_bucket == 'mlops-platform-bucket'
    assert config.cloudwatch_namespace == 'MLOps/Platform'
