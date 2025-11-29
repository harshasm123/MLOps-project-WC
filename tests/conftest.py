"""
Pytest configuration and shared fixtures for MLOps platform tests.
"""

import pytest
from datetime import datetime
from src.models.data_models import (
    ModelMetadata, ApprovalStatus, BaselineStatistics,
    FeatureStats, PipelineConfig, EvaluationMetrics
)


@pytest.fixture
def sample_model_metadata():
    """Fixture providing sample model metadata."""
    return ModelMetadata(
        model_group="test-model-group",
        version="v1.0.0",
        algorithm="RandomForest",
        framework="sklearn",
        framework_version="1.3.0",
        training_job_id="job-123",
        dataset_version="v1.0",
        hyperparameters={"n_estimators": 100, "max_depth": 10},
        metrics={"accuracy": 0.85, "f1_score": 0.82},
        created_at=datetime.now(),
        created_by="test-user",
        approval_status=ApprovalStatus.PENDING,
        tags={"environment": "test"}
    )


@pytest.fixture
def sample_feature_stats():
    """Fixture providing sample feature statistics."""
    return FeatureStats(
        feature_name="age",
        data_type="numeric",
        mean=45.5,
        std=12.3,
        min=18.0,
        max=90.0,
        missing_count=5,
        unique_count=50
    )


@pytest.fixture
def sample_baseline_statistics(sample_feature_stats):
    """Fixture providing sample baseline statistics."""
    return BaselineStatistics(
        dataset_version="v1.0",
        created_at=datetime.now(),
        feature_statistics={"age": sample_feature_stats}
    )


@pytest.fixture
def sample_pipeline_config():
    """Fixture providing sample pipeline configuration."""
    return PipelineConfig(
        pipeline_name="test-pipeline",
        pipeline_type="training",
        instance_type="ml.m5.large",
        instance_count=1,
        max_runtime_seconds=3600,
        input_data_uri="s3://bucket/input",
        output_data_uri="s3://bucket/output",
        role_arn="arn:aws:iam::123456789012:role/SageMakerRole"
    )


@pytest.fixture
def sample_evaluation_metrics():
    """Fixture providing sample evaluation metrics."""
    return EvaluationMetrics(
        accuracy=0.85,
        precision=0.83,
        recall=0.87,
        f1_score=0.85,
        auc_roc=0.90,
        confusion_matrix=[[45, 5], [3, 47]]
    )
