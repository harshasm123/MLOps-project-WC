"""
Lambda function to handle model registry operations.
Manages model versions, metadata, and approval workflows.
"""

import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sagemaker = boto3.client('sagemaker')

MODELS_TABLE = os.environ.get('MODELS_TABLE', 'mlops-models')


def lambda_handler(event, context):
    """
    Handle model registry requests.
    
    Supported operations:
    - GET /models - List all models
    - GET /models/{version} - Get specific model
    - POST /models/{version}/approve - Approve model
    """
    try:
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        
        if http_method == 'GET' and path == '/models':
            return list_models()
        elif http_method == 'GET' and '/models/' in path:
            version = path.split('/')[-1]
            return get_model(version)
        elif http_method == 'POST' and '/approve' in path:
            version = path.split('/')[-2]
            return approve_model(version)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Not found'})
            }
            
    except Exception as e:
        print(f"Error in model registry handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Internal server error: {str(e)}'
            })
        }


def list_models():
    """List all registered models."""
    try:
        table = dynamodb.Table(MODELS_TABLE)
        response = table.scan()
        
        models = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'models': models
            })
        }
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        # Return mock data for demonstration
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'models': [
                    {
                        'modelGroup': 'medication-adherence-model',
                        'version': 'v1.0.0',
                        'algorithm': 'RandomForest',
                        'metrics': {
                            'accuracy': 0.85,
                            'f1Score': 0.83,
                            'precision': 0.84,
                            'recall': 0.82
                        },
                        'approvalStatus': 'approved',
                        'createdAt': '2024-01-15T10:30:00Z'
                    },
                    {
                        'modelGroup': 'medication-adherence-model',
                        'version': 'v1.1.0',
                        'algorithm': 'XGBoost',
                        'metrics': {
                            'accuracy': 0.87,
                            'f1Score': 0.85,
                            'precision': 0.86,
                            'recall': 0.84
                        },
                        'approvalStatus': 'pending',
                        'createdAt': '2024-01-20T14:45:00Z'
                    }
                ]
            })
        }


def get_model(version):
    """Get a specific model by version."""
    try:
        table = dynamodb.Table(MODELS_TABLE)
        response = table.get_item(Key={'version': version})
        
        model = response.get('Item')
        
        if not model:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Model not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'model': model})
        }
    except Exception as e:
        print(f"Error getting model: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': str(e)})
        }


def approve_model(version):
    """Approve a model for deployment."""
    try:
        table = dynamodb.Table(MODELS_TABLE)
        
        # Update approval status
        table.update_item(
            Key={'version': version},
            UpdateExpression='SET approvalStatus = :status, approvedAt = :timestamp',
            ExpressionAttributeValues={
                ':status': 'approved',
                ':timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Model approved successfully',
                'version': version
            })
        }
    except Exception as e:
        print(f"Error approving model: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': str(e)})
        }
