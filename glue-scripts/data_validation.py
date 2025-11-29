"""
AWS Glue Job for Data Validation
Validates incoming datasets for quality and schema compliance
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, count, when, isnan, isnull
import boto3

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# CloudWatch client for metrics
cloudwatch = boto3.client('cloudwatch')

def validate_schema(df, expected_columns):
    """Validate that dataframe has expected columns."""
    actual_columns = set(df.columns)
    expected_columns = set(expected_columns)
    
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    if extra_columns:
        print(f"Warning: Extra columns found: {extra_columns}")
    
    return True

def check_data_quality(df):
    """Check data quality metrics."""
    total_rows = df.count()
    
    quality_metrics = {
        'total_rows': total_rows,
        'missing_values': {},
        'duplicate_rows': 0
    }
    
    # Check for missing values in each column
    for column in df.columns:
        missing_count = df.filter(
            col(column).isNull() | isnan(col(column))
        ).count()
        
        missing_percentage = (missing_count / total_rows) * 100
        quality_metrics['missing_values'][column] = {
            'count': missing_count,
            'percentage': missing_percentage
        }
        
        # Alert if missing values exceed threshold
        if missing_percentage > 20:
            print(f"WARNING: Column '{column}' has {missing_percentage:.2f}% missing values")
    
    # Check for duplicate rows
    duplicate_count = total_rows - df.dropDuplicates().count()
    quality_metrics['duplicate_rows'] = duplicate_count
    
    if duplicate_count > 0:
        print(f"WARNING: Found {duplicate_count} duplicate rows")
    
    return quality_metrics

def publish_metrics(metrics):
    """Publish data quality metrics to CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace='MLOps/DataQuality',
            MetricData=[
                {
                    'MetricName': 'TotalRows',
                    'Value': metrics['total_rows'],
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'DuplicateRows',
                    'Value': metrics['duplicate_rows'],
                    'Unit': 'Count'
                }
            ]
        )
        print("Metrics published to CloudWatch")
    except Exception as e:
        print(f"Error publishing metrics: {str(e)}")

# Main validation logic
try:
    print(f"Reading data from: {args['input_path']}")
    
    # Read data
    df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(args['input_path'])
    
    print(f"Loaded {df.count()} rows with {len(df.columns)} columns")
    
    # Expected schema for diabetic dataset
    expected_columns = [
        'patient_id',
        'age',
        'gender',
        'medication_brand',
        'prescription_date',
        'refill_count',
        'adherence_history'
    ]
    
    # Validate schema
    print("Validating schema...")
    validate_schema(df, expected_columns)
    print("✓ Schema validation passed")
    
    # Check data quality
    print("Checking data quality...")
    quality_metrics = check_data_quality(df)
    print("✓ Data quality check completed")
    
    # Publish metrics
    publish_metrics(quality_metrics)
    
    # Write validated data
    print(f"Writing validated data to: {args['output_path']}")
    df.write.mode("overwrite") \
        .format("parquet") \
        .save(args['output_path'])
    
    print("✓ Data validation completed successfully")
    
    # Set job status
    job.commit()
    
except Exception as e:
    print(f"✗ Data validation failed: {str(e)}")
    raise
