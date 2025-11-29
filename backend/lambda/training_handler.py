"""
Lambda function to handle training pipeline requests.
Triggers SageMaker training jobs for medication adherence prediction.
"""

import json
import boto3
import os
from datetime import datetime

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
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        dataset_uri = body.get('datasetUri')
        model_name = body.get('modelName', 'medication-adherence-model')
        algorithm = body.get('algorithm', 'RandomForest')
        instance_type = body.get('instanceType', 'ml.m5.xlarge')
        max_runtime = body.get('maxRuntime', 3600)
        
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
        
    except Exception as e:
        print(f"Error starting training job: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Failed to start training job: {str(e)}'
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
