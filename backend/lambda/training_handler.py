"""
Lambda function to handle training pipeline requests.
Triggers SageMaker training jobs for medication adherence prediction.
"""

import json
import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sagemaker = boto3.client('sagemaker')
s3 = boto3.client('s3')

SAGEMAKER_ROLE = os.environ.get('SAGEMAKER_ROLE_ARN')
MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'mlops-model-registry')


def lambda_handler(event, context):
    """
    Handle training pipeline start requests.
    
    Expected input:
    {
        "datasetUri": "s3://bucket/path/to/data.csv",
        "modelName": "medication-adherence-model",
        "algorithm": "RandomForest",
        "instanceType": "ml.m5.xlarge",
        "maxRuntime": 3600
    }
    """
    try:
        logger.info(f"Received training request: {json.dumps(event, default=str)}")
        
        # Parse request body
        if 'body' not in event:
            raise ValueError("Missing request body")
            
        body = json.loads(event.get('body', '{}'))
        
        # Validate required parameters
        dataset_uri = body.get('datasetUri')
        if not dataset_uri or not dataset_uri.startswith('s3://'):
            raise ValueError("Valid S3 dataset URI is required")
            
        model_name = validate_model_name(body.get('modelName', 'medication-adherence-model'))
        algorithm = validate_algorithm(body.get('algorithm', 'RandomForest'))
        instance_type = validate_instance_type(body.get('instanceType', 'ml.m5.xlarge'))
        max_runtime = min(int(body.get('maxRuntime', 3600)), 86400)  # Max 24 hours
        
        # Generate unique training job name
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        training_job_name = f"{model_name}-{timestamp}"
        
        # Configure training job
        training_params = {
            'TrainingJobName': training_job_name,
            'RoleArn': SAGEMAKER_ROLE,
            'AlgorithmSpecification': {
                'TrainingImage': get_training_image(algorithm),
                'TrainingInputMode': 'File'
            },
            'InputDataConfig': [
                {
                    'ChannelName': 'training',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': dataset_uri,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    },
                    'ContentType': 'text/csv'
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': f's3://{MODEL_BUCKET}/models/{model_name}/'
            },
            'ResourceConfig': {
                'InstanceType': instance_type,
                'InstanceCount': 1,
                'VolumeSizeInGB': 30
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': max_runtime
            },
            'HyperParameters': get_hyperparameters(algorithm),
            'Tags': [
                {'Key': 'Project', 'Value': 'MLOps-Platform'},
                {'Key': 'UseCase', 'Value': 'MedicationAdherence'}
            ]
        }
        
        # Start training job
        response = sagemaker.create_training_job(**training_params)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'trainingJobId': training_job_name,
                'status': 'InProgress',
                'message': 'Training job started successfully',
                'trainingJobArn': response['TrainingJobArn']
            })
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'ValidationError',
                'message': str(e)
            })
        }
    except (ClientError, BotoCoreError) as e:
        logger.error(f"AWS service error: {str(e)}")
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'ServiceError',
                'message': 'AWS service temporarily unavailable'
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'InternalError',
                'message': 'Internal server error'
            })
        }


def get_training_image(algorithm):
    """Get the appropriate SageMaker training image for the algorithm."""
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # SageMaker built-in algorithm images
    images = {
        'XGBoost': f'683313688378.dkr.ecr.{region}.amazonaws.com/sagemaker-xgboost:1.5-1',
        'RandomForest': f'683313688378.dkr.ecr.{region}.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3',
        'LogisticRegression': f'683313688378.dkr.ecr.{region}.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3'
    }
    
    return images.get(algorithm, images['RandomForest'])


def get_hyperparameters(algorithm):
    """Get default hyperparameters for the algorithm."""
    hyperparameters = {
        'RandomForest': {
            'n_estimators': '100',
            'max_depth': '10',
            'min_samples_split': '2'
        },
        'XGBoost': {
            'max_depth': '5',
            'eta': '0.2',
            'objective': 'binary:logistic',
            'num_round': '100'
        },
        'LogisticRegression': {
            'C': '1.0',
            'max_iter': '100'
        }
    }
    
    return hyperparameters.get(algorithm, hyperparameters['RandomForest'])


def validate_model_name(name):
    """Validate and sanitize model name."""
    if not name or not isinstance(name, str):
        raise ValueError("Model name must be a non-empty string")
    
    # Remove special characters and limit length
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', name)[:50]
    if not sanitized:
        raise ValueError("Invalid model name")
    return sanitized


def validate_algorithm(algorithm):
    """Validate algorithm choice."""
    allowed_algorithms = ['RandomForest', 'XGBoost', 'LogisticRegression']
    if algorithm not in allowed_algorithms:
        raise ValueError(f"Algorithm must be one of: {allowed_algorithms}")
    return algorithm


def validate_instance_type(instance_type):
    """Validate SageMaker instance type."""
    allowed_types = [
        'ml.m5.large', 'ml.m5.xlarge', 'ml.m5.2xlarge',
        'ml.c5.large', 'ml.c5.xlarge', 'ml.c5.2xlarge'
    ]
    if instance_type not in allowed_types:
        raise ValueError(f"Instance type must be one of: {allowed_types}")
    return instance_type