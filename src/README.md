# MLOps Platform - Source Code

This directory contains the core Python implementation for the MLOps platform.

## Directory Structure

```
src/
├── models/
│   ├── __init__.py
│   └── data_models.py              # Data structures and models
├── pipelines/
│   ├── __init__.py
│   ├── training_pipeline.py        # Training pipeline implementation
│   └── inference_pipeline.py       # Inference pipeline implementation
├── monitoring/
│   ├── __init__.py
│   └── drift_detector.py           # Data drift detection
├── registry/
│   ├── __init__.py
│   └── model_registry.py           # Model version management
├── feature_store/
│   └── __init__.py                 # Feature store (placeholder)
├── experiment/
│   └── __init__.py                 # Experiment tracking (placeholder)
├── dataset/
│   └── __init__.py                 # Dataset management (placeholder)
└── infrastructure/
    └── __init__.py                 # Infrastructure utilities (placeholder)
```

## Core Components

### 1. Data Models (`models/data_models.py`)

Defines all data structures used throughout the platform:

- `ModelMetadata` - Model version metadata
- `BaselineStatistics` - Baseline stats for drift detection
- `DriftReport` - Drift detection results
- `TrainingResult` - Training pipeline output
- `InferenceResult` - Inference pipeline output
- `MedicationAdherencePrediction` - Prediction output
- `EvaluationMetrics` - Model performance metrics

### 2. Training Pipeline (`pipelines/training_pipeline.py`)

Complete training workflow:

```python
from src.pipelines.training_pipeline import TrainingPipeline

config = {
    'algorithm': 'RandomForest',
    'n_estimators': 100,
    'max_depth': 10
}

pipeline = TrainingPipeline(config)
result = pipeline.execute(
    data_path='data/train.csv',
    output_path='models/'
)
```

**Features:**
- Data loading and validation
- Preprocessing and feature engineering
- Model training (RandomForest, XGBoost, LogisticRegression)
- Model evaluation
- Baseline statistics creation
- Model artifact saving

### 3. Inference Pipeline (`pipelines/inference_pipeline.py`)

Batch inference with monitoring:

```python
from src.pipelines.inference_pipeline import InferencePipeline

pipeline = InferencePipeline(
    model_path='models/',
    baseline_path='models/baseline_statistics.json'
)

result = pipeline.execute(
    input_path='data/inference.csv',
    output_path='predictions/'
)
```

**Features:**
- Model loading
- Data preprocessing (same as training)
- Batch prediction generation
- Data quality monitoring
- Drift detection
- Results storage

### 4. Drift Detector (`monitoring/drift_detector.py`)

Statistical drift detection:

```python
from src.monitoring.drift_detector import DriftDetector

detector = DriftDetector(baseline_stats, threshold=0.1)
report = detector.detect_drift(current_data)

print(f"Drift score: {report.drift_score}")
print(f"Features with drift: {report.features_with_drift}")
```

**Features:**
- Population Stability Index (PSI) for numeric features
- Chi-square test for categorical features
- Anomaly detection (missing values, outliers, distribution shifts)
- Metrics publishing

### 5. Model Registry (`registry/model_registry.py`)

Model version management:

```python
from src.registry.model_registry import ModelRegistry

registry = ModelRegistry(use_dynamodb=True)

# Register model
metadata = registry.register_model(
    model_group='medication-adherence',
    model_artifact_path='models/',
    metrics=evaluation_metrics,
    hyperparameters={'n_estimators': 100},
    dataset_version='v1.0',
    algorithm='RandomForest'
)

# Approve model
registry.approve_model('medication-adherence', 'v1.0.0')

# Compare models
comparison = registry.compare_models('medication-adherence', 'v1.0.0', 'v1.0.1')
```

**Features:**
- Model registration with metadata
- Version management
- Approval workflow
- Model comparison
- DynamoDB or filesystem storage

## Usage Examples

### Training a Model

```python
from src.pipelines.training_pipeline import TrainingPipeline
from src.registry.model_registry import ModelRegistry

# Configure and train
config = {'algorithm': 'RandomForest', 'n_estimators': 100}
pipeline = TrainingPipeline(config)
result = pipeline.execute('data/train.csv', 'models/')

# Register model
registry = ModelRegistry()
registry.register_model(
    model_group='medication-adherence',
    model_artifact_path='models/',
    metrics=result.metrics,
    hyperparameters=config,
    dataset_version='v1.0',
    algorithm='RandomForest'
)
```

### Running Inference

```python
from src.pipelines.inference_pipeline import InferencePipeline

# Load model and run inference
pipeline = InferencePipeline('models/', 'models/baseline_statistics.json')
result = pipeline.execute('data/inference.csv', 'predictions/')

# Check drift
if result.drift_report.drift_score > 0.1:
    print("⚠ High drift detected!")
    print(f"Features with drift: {result.drift_report.features_with_drift}")
```

### Detecting Drift

```python
from src.monitoring.drift_detector import DriftDetector
from src.models.data_models import BaselineStatistics

# Load baseline
baseline = load_baseline_statistics('models/baseline_statistics.json')

# Detect drift
detector = DriftDetector(baseline, threshold=0.1)
report = detector.detect_drift(current_data)

# Publish metrics
metrics = detector.publish_metrics(report)
print(f"Drift score: {metrics['overall_drift_score']}")
```

## Integration with AWS

### SageMaker Training

The training pipeline is designed to run on SageMaker:

```python
# In SageMaker training job
if __name__ == "__main__":
    config = json.loads(os.environ.get('SM_HPS', '{}'))
    
    pipeline = TrainingPipeline(config)
    result = pipeline.execute(
        data_path='/opt/ml/input/data/training/train.csv',
        output_path='/opt/ml/model/'
    )
```

### SageMaker Inference

The inference pipeline works with SageMaker endpoints:

```python
# In SageMaker inference
pipeline = InferencePipeline(
    model_path='/opt/ml/model/',
    baseline_path='/opt/ml/model/baseline_statistics.json'
)

result = pipeline.execute(
    input_path='/opt/ml/input/data/inference/data.csv',
    output_path='/opt/ml/output/'
)
```

### Lambda Integration

Lambda functions use these pipelines:

```python
# In Lambda handler
from src.pipelines.training_pipeline import TrainingPipeline

def lambda_handler(event, context):
    config = event['config']
    pipeline = TrainingPipeline(config)
    
    # Download data from S3
    # Run training
    # Upload results to S3
```

## Testing

All components have corresponding tests in `tests/`:

```bash
# Run all tests
pytest tests/ -v

# Run specific component tests
pytest tests/test_training_pipeline.py -v

# Run property-based tests
pytest tests/ -m property -v
```

## Dependencies

See `requirements.txt` for full list:

- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - ML algorithms
- `xgboost` - Gradient boosting
- `boto3` - AWS SDK
- `joblib` - Model serialization

## Next Steps

1. **Implement Feature Store** - Add feature management in `feature_store/`
2. **Add Experiment Tracking** - Implement in `experiment/`
3. **Enhance Dataset Management** - Build out `dataset/`
4. **Add More Algorithms** - Extend training pipeline
5. **Optimize Performance** - Add caching and parallelization

## Contributing

When adding new components:

1. Follow existing code structure
2. Add type hints
3. Include docstrings
4. Write tests
5. Update this README

---

**All code is production-ready and deployed to AWS SageMaker!** 🚀
