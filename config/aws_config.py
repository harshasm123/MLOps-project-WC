"""
AWS configuration management for the MLOps platform.
Handles AWS resource configuration including regions, buckets, and IAM roles.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AWSConfig:
    """AWS configuration settings."""
    region: str
    s3_bucket: str
    model_registry_bucket: str
    data_bucket: str
    sagemaker_role_arn: str
    cloudwatch_namespace: str
    
    @classmethod
    def from_env(cls) -> 'AWSConfig':
        """Load configuration from environment variables."""
        return cls(
            region=os.getenv('AWS_REGION', 'us-east-1'),
            s3_bucket=os.getenv('MLOPS_S3_BUCKET', 'mlops-platform-bucket'),
            model_registry_bucket=os.getenv('MODEL_REGISTRY_BUCKET', 'mlops-model-registry'),
            data_bucket=os.getenv('DATA_BUCKET', 'mlops-data-bucket'),
            sagemaker_role_arn=os.getenv('SAGEMAKER_ROLE_ARN', ''),
            cloudwatch_namespace=os.getenv('CLOUDWATCH_NAMESPACE', 'MLOps/Platform')
        )
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.sagemaker_role_arn:
            raise ValueError("SAGEMAKER_ROLE_ARN must be set")
        if not self.region:
            raise ValueError("AWS_REGION must be set")
        return True


def get_config() -> AWSConfig:
    """Get the current AWS configuration."""
    config = AWSConfig.from_env()
    config.validate()
    return config
