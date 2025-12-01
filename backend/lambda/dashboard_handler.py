"""
Dashboard handler Lambda function.
Provides system statistics and health metrics for the MLOps platform.
"""

import json
import boto3
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
sagemaker = boto3.client('sagemaker')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    """
    Handle dashboard statistics requests.
    
    Returns system metrics including:
    - Total models in registry
    - Active training jobs
    - Recent predictions count
    - Data drift alerts
    """
    try:
        logger.info("Fetching dashboard statistics")
        
        # Get statistics
        stats = {
            'totalModels': get_total_models(),
            'activeTrainingJobs': get_active_training_jobs(),
            'recentPredictions': get_recent_predictions(),
            'driftAlerts': get_drift_alerts(),
            'lastUpdated': datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'max-age=300'  # Cache for 5 minutes
            },
            'body': json.dumps(stats)
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'InternalError',
                'message': 'Failed to fetch dashboard statistics'
            })
        }


def get_total_models():
    """Get total number of models in registry."""
    try:
        table_name = 'mlops-platform-models-dev'  # Should come from env var
        table = dynamodb.Table(table_name)
        response = table.scan(Select='COUNT')
        return response.get('Count', 0)
    except Exception as e:
        logger.warning(f"Could not get model count: {str(e)}")
        return 0


def get_active_training_jobs():
    """Get number of active training jobs."""
    try:
        response = sagemaker.list_training_jobs(
            StatusEquals='InProgress',
            MaxResults=100
        )
        return len(response.get('TrainingJobSummaries', []))
    except Exception as e:
        logger.warning(f"Could not get training job count: {str(e)}")
        return 0


def get_recent_predictions():
    """Get number of recent predictions (last 24 hours)."""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        response = cloudwatch.get_metric_statistics(
            Namespace='MLOps/Predictions',
            MetricName='PredictionCount',
            Dimensions=[],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        total = sum(point['Sum'] for point in response.get('Datapoints', []))
        return int(total)
    except Exception as e:
        logger.warning(f"Could not get prediction count: {str(e)}")
        return 0


def get_drift_alerts():
    """Get number of active drift alerts."""
    try:
        # In a real implementation, this would check CloudWatch alarms
        # or a dedicated alerts table
        return 0  # Placeholder
    except Exception as e:
        logger.warning(f"Could not get drift alerts: {str(e)}")
        return 0