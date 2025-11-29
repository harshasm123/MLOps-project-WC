"""
AWS Glue Job for Data Preprocessing
Preprocesses validated data for ML training
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, when, datediff, current_date, lit
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml import Pipeline

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

def handle_missing_values(df):
    """Handle missing values in the dataset."""
    print("Handling missing values...")
    
    # Fill numeric columns with median
    numeric_columns = ['age', 'refill_count']
    for column in numeric_columns:
        median_value = df.approxQuantile(column, [0.5], 0.01)[0]
        df = df.fillna({column: median_value})
    
    # Fill categorical columns with mode
    categorical_columns = ['gender', 'medication_brand']
    for column in categorical_columns:
        mode_value = df.groupBy(column).count().orderBy('count', ascending=False).first()[0]
        df = df.fillna({column: mode_value})
    
    return df

def create_features(df):
    """Create additional features for ML model."""
    print("Creating features...")
    
    # Calculate days since prescription
    df = df.withColumn(
        'days_since_prescription',
        datediff(current_date(), col('prescription_date'))
    )
    
    # Create age groups
    df = df.withColumn(
        'age_group',
        when(col('age') < 30, 'young')
        .when((col('age') >= 30) & (col('age') < 50), 'middle')
        .otherwise('senior')
    )
    
    # Create refill frequency category
    df = df.withColumn(
        'refill_frequency',
        when(col('refill_count') < 2, 'low')
        .when((col('refill_count') >= 2) & (col('refill_count') < 5), 'medium')
        .otherwise('high')
    )
    
    # Create adherence risk score (simplified)
    df = df.withColumn(
        'adherence_risk_score',
        when(col('adherence_history') < 0.5, 3)  # High risk
        .when((col('adherence_history') >= 0.5) & (col('adherence_history') < 0.8), 2)  # Medium risk
        .otherwise(1)  # Low risk
    )
    
    return df

def encode_categorical_features(df):
    """Encode categorical features for ML."""
    print("Encoding categorical features...")
    
    categorical_columns = ['gender', 'medication_brand', 'age_group', 'refill_frequency']
    
    indexers = [
        StringIndexer(inputCol=col, outputCol=f"{col}_index")
        for col in categorical_columns
    ]
    
    encoders = [
        OneHotEncoder(inputCol=f"{col}_index", outputCol=f"{col}_encoded")
        for col in categorical_columns
    ]
    
    # Create pipeline
    pipeline = Pipeline(stages=indexers + encoders)
    model = pipeline.fit(df)
    df = model.transform(df)
    
    return df

def create_train_test_split(df, train_ratio=0.8):
    """Split data into training and testing sets."""
    print(f"Splitting data (train: {train_ratio}, test: {1-train_ratio})...")
    
    # Add random column for splitting
    df = df.withColumn('random', lit(None).cast('double'))
    df = df.withColumn('random', when(col('random').isNull(), 
                                      (col('patient_id').cast('long') % 100) / 100.0))
    
    train_df = df.filter(col('random') < train_ratio)
    test_df = df.filter(col('random') >= train_ratio)
    
    print(f"Training set: {train_df.count()} rows")
    print(f"Testing set: {test_df.count()} rows")
    
    return train_df, test_df

# Main preprocessing logic
try:
    print(f"Reading validated data from: {args['input_path']}")
    
    # Read validated data
    df = spark.read.format("parquet").load(args['input_path'])
    
    print(f"Loaded {df.count()} rows")
    
    # Handle missing values
    df = handle_missing_values(df)
    print("✓ Missing values handled")
    
    # Create features
    df = create_features(df)
    print("✓ Features created")
    
    # Encode categorical features
    df = encode_categorical_features(df)
    print("✓ Categorical features encoded")
    
    # Create train/test split
    train_df, test_df = create_train_test_split(df)
    print("✓ Train/test split completed")
    
    # Write preprocessed data
    train_output = f"{args['output_path']}/train"
    test_output = f"{args['output_path']}/test"
    
    print(f"Writing training data to: {train_output}")
    train_df.write.mode("overwrite").format("parquet").save(train_output)
    
    print(f"Writing testing data to: {test_output}")
    test_df.write.mode("overwrite").format("parquet").save(test_output)
    
    print("✓ Data preprocessing completed successfully")
    
    # Commit job
    job.commit()
    
except Exception as e:
    print(f"✗ Data preprocessing failed: {str(e)}")
    raise
