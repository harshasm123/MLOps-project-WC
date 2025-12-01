"""
Model Registry Lambda handler for MLOps Platform.
Manages model versions, metadata, and approval workflows.
"""

import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Handle model registry operations.
    
    Supported operations:
    - GET /models - List all models
    - GET /models/{version} - Get specific model
    - POST /models - Register new model
    - PUT /models/{version}/approve - Approve model
    """
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/models')
        
        if http_method == 'GET' and path == '/models':
            return list_models()
        elif http_method == 'GET' and '/models/' in path:
            version = path.split('/')[-1]
            return get_model(version)
        elif http_method == 'POST' and path == '/models':
            body = json.loads(event.get('body', '{}'))
            return register_model(body)
        elif http_method == 'PUT' and 'approve' in path:
            version = path.split('/')[-2]
            return approve_model(version)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Not Found'})
            }
            
    except Exception as e:
        logger.error(f"Error in model registry: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'InternalError',
                'message': 'Model registry operation failed'
            })
        }


def list_models():
    """List all registered models."""
    try:
        table_name = 'mlops-platform-models-dev'  # Should come from env var
        table = dynamodb.Table(table_name)
        
        response = table.scan()
        models = response.get('Items', [])
        
        # Sort by creation date
        models.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'models': models,
                'count': len(models)
            })
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise


def get_model(version):
    """Get specific model by version."""
    try:
        table_name = 'mlops-platform-models-dev'
        table = dynamodb.Table(table_name)
        
        response = table.get_item(Key={'version': version})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Model not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response['Item'])
        }
        
    except Exception as e:
        logger.error(f"Error getting model {version}: {str(e)}")
        raise


def register_model(model_data):
    """Register a new model version."""
    try:
        table_name = 'mlops-platform-models-dev'
        table = dynamodb.Table(table_name)
        
        # Generate version if not provided
        version = model_data.get('version', f"v{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        model_item = {
            'version': version,
            'modelGroup': model_data.get('modelGroup', 'medication-adherence'),
            'algorithm': model_data.get('algorithm', 'RandomForest'),
            'accuracy': float(model_data.get('accuracy', 0.0)),
            'precision': float(model_data.get('precision', 0.0)),
            'recall': float(model_data.get('recall', 0.0)),
            'f1Score': float(model_data.get('f1Score', 0.0)),
            'aucRoc': float(model_data.get('aucRoc', 0.0)),
            'modelUri': model_data.get('modelUri', ''),
            'trainingJobName': model_data.get('trainingJobName', ''),
            'status': 'Pending',
            'createdAt': datetime.utcnow().isoformat(),
            'createdBy': model_data.get('createdBy', 'system')
        }
        
        table.put_item(Item=model_item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Model registered successfully',
                'version': version,
                'model': model_item
            })
        }
        
    except Exception as e:
        logger.error(f"Error registering model: {str(e)}")
        raise


def approve_model(version):
    """Approve a model version for production use."""
    try:
        table_name = 'mlops-platform-models-dev'
        table = dynamodb.Table(table_name)
        
        # Update model status
        response = table.update_item(
            Key={'version': version},
            UpdateExpression='SET #status = :status, approvedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'Approved',
                ':timestamp': datetime.utcnow().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Model approved successfully',
                'model': response['Attributes']
            })
        }
        
    except Exception as e:
        logger.error(f"Error approving model {version}: {str(e)}")
        raise