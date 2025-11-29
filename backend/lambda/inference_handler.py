"""
Lambda function to handle inference pipeline requests.
Runs batch predictions using deployed SageMaker models.
"""

import json
import boto3
import os
from datetime import datetime
import uuid

sagemaker_runtime = boto3.client('sagemaker-runtime')
sagemaker = boto3.client('sagemaker')
s3 = boto3.client('s3')

MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'mlops-model-registry')
DATA_BUCKET = os.environ.get('DATA_BUCKET', 'mlops-data-bucket')


def lambda_handler(event, context):
    """
    Handle inference requests.
    
    Expected input:
    {
        "inputDataUri": "s3://bucket/path/to/input.csv",
        "modelVersion": "latest"
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        input_data_uri = body.get('inputDataUri')
        model_version = body.get('modelVersion', 'latest')
        
        # Get the model endpoint
        endpoint_name = get_model_endpoint(model_version)
        
        if not endpoint_name:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'No deployed model found'
                })
            }
        
        # Load input data from S3
        input_data = load_data_from_s3(input_data_uri)
        
        # Run batch inference
        predictions = []
        for record in input_data[:100]:  # Limit to 100 for demo
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Body=record
            )
            
            prediction = json.loads(response['Body'].read().decode())
            predictions.append({
                'patientId': record.get('patient_id', str(uuid.uuid4())),
                'medicationBrand': record.get('medication_brand', 'Unknown'),
                'nonAdherenceProbability': prediction.get('probability', 0.5),
                'confidenceScore': prediction.get('confidence', 0.8),
                'riskFactors': prediction.get('risk_factors', [])
            })
        
        # Calculate drift score (simplified)
        drift_score = calculate_drift_score(input_data)
        
        # Store results
        inference_id = str(uuid.uuid4())
        results_uri = f's3://{DATA_BUCKET}/inference-results/{inference_id}.json'
        store_results(results_uri, predictions)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'inferenceJobId': inference_id,
                'predictionCount': len(predictions),
                'predictions': predictions,
                'driftScore': drift_score,
                'resultsUri': results_uri,
                'status': 'completed'
            })
        }
        
    except Exception as e:
        print(f"Error running inference: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Failed to run inference: {str(e)}'
            })
        }


def get_model_endpoint(model_version):
    """Get the SageMaker endpoint for the specified model version."""
    try:
        # List endpoints and find the one for our model
        response = sagemaker.list_endpoints(
            StatusEquals='InService',
            MaxResults=10
        )
        
        endpoints = response.get('Endpoints', [])
        if endpoints:
            return endpoints[0]['EndpointName']
        
        return None
    except Exception as e:
        print(f"Error getting endpoint: {str(e)}")
        return None


def load_data_from_s3(s3_uri):
    """Load data from S3."""
    # Parse S3 URI
    parts = s3_uri.replace('s3://', '').split('/', 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ''
    
    # Load data
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8')
    
    # Parse CSV (simplified)
    lines = data.strip().split('\n')
    headers = lines[0].split(',')
    
    records = []
    for line in lines[1:]:
        values = line.split(',')
        record = dict(zip(headers, values))
        records.append(record)
    
    return records


def calculate_drift_score(data):
    """Calculate a simplified drift score."""
    # In production, this would compare against baseline statistics
    # For now, return a random score for demonstration
    import random
    return random.uniform(0.01, 0.15)


def store_results(s3_uri, results):
    """Store inference results to S3."""
    parts = s3_uri.replace('s3://', '').split('/', 1)
    bucket = parts[0]
    key = parts[1]
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(results, indent=2),
        ContentType='application/json'
    )
