"""
Model Registry for MLOps Platform
Manages model versions, metadata, and approval workflows
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3

from src.models.data_models import ModelMetadata, ApprovalStatus, EvaluationMetrics


class ModelRegistry:
    """Manages ML model versions and metadata."""
    
    def __init__(self, registry_path: str = None, use_dynamodb: bool = False):
        """
        Initialize model registry.
        
        Args:
            registry_path: Local path for model registry (if not using DynamoDB)
            use_dynamodb: Whether to use DynamoDB for storage
        """
        self.registry_path = registry_path or '/tmp/model_registry'
        self.use_dynamodb = use_dynamodb
        
        if use_dynamodb:
            self.dynamodb = boto3.resource('dynamodb')
            self.table_name = os.environ.get('MODELS_TABLE', 'mlops-models')
            self.table = self.dynamodb.Table(self.table_name)
        else:
            os.makedirs(self.registry_path, exist_ok=True)
    
    def register_model(
        self,
        model_group: str,
        model_artifact_path: str,
        metrics: EvaluationMetrics,
        hyperparameters: Dict[str, Any],
        dataset_version: str,
        algorithm: str,
        framework: str = "sklearn",
        framework_version: str = "1.3.0",
        created_by: str = "system",
        tags: Dict[str, str] = None
    ) -> ModelMetadata:
        """
        Register a new model version.
        
        Args:
            model_group: Model group name
            model_artifact_path: Path to model artifacts
            metrics: Evaluation metrics
            hyperparameters: Model hyperparameters
            dataset_version: Version of training dataset
            algorithm: Algorithm name
            framework: ML framework
            framework_version: Framework version
            created_by: User who created the model
            tags: Additional tags
            
        Returns:
            ModelMetadata object
        """
        # Generate version
        version = self._generate_version(model_group)
        training_job_id = f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        metadata = ModelMetadata(
            model_group=model_group,
            version=version,
            algorithm=algorithm,
            framework=framework,
            framework_version=framework_version,
            training_job_id=training_job_id,
            dataset_version=dataset_version,
            hyperparameters=hyperparameters,
            metrics={
                'accuracy': metrics.accuracy,
                'precision': metrics.precision,
                'recall': metrics.recall,
                'f1_score': metrics.f1_score,
                'auc_roc': metrics.auc_roc
            },
            created_at=datetime.now(),
            created_by=created_by,
            approval_status=ApprovalStatus.PENDING,
            tags=tags or {}
        )
        
        # Save metadata
        self._save_metadata(metadata)
        
        print(f"✓ Model registered: {model_group} version {version}")
        return metadata
    
    def get_model(self, model_group: str, version: Optional[str] = None) -> Optional[ModelMetadata]:
        """
        Get model metadata.
        
        Args:
            model_group: Model group name
            version: Model version (None for latest)
            
        Returns:
            ModelMetadata object or None
        """
        if version is None:
            # Get latest version
            versions = self.list_model_versions(model_group)
            if not versions:
                return None
            version = versions[0].version
        
        return self._load_metadata(model_group, version)
    
    def list_model_versions(self, model_group: str) -> List[ModelMetadata]:
        """
        List all versions of a model group.
        
        Args:
            model_group: Model group name
            
        Returns:
            List of ModelMetadata objects
        """
        if self.use_dynamodb:
            return self._list_from_dynamodb(model_group)
        else:
            return self._list_from_filesystem(model_group)
    
    def approve_model(self, model_group: str, version: str) -> bool:
        """
        Approve a model for deployment.
        
        Args:
            model_group: Model group name
            version: Model version
            
        Returns:
            True if successful
        """
        metadata = self.get_model(model_group, version)
        if not metadata:
            return False
        
        metadata.approval_status = ApprovalStatus.APPROVED
        self._save_metadata(metadata)
        
        print(f"✓ Model approved: {model_group} version {version}")
        return True
    
    def reject_model(self, model_group: str, version: str) -> bool:
        """
        Reject a model.
        
        Args:
            model_group: Model group name
            version: Model version
            
        Returns:
            True if successful
        """
        metadata = self.get_model(model_group, version)
        if not metadata:
            return False
        
        metadata.approval_status = ApprovalStatus.REJECTED
        self._save_metadata(metadata)
        
        print(f"✓ Model rejected: {model_group} version {version}")
        return True
    
    def compare_models(self, model_group: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two model versions.
        
        Args:
            model_group: Model group name
            version1: First version
            version2: Second version
            
        Returns:
            Comparison dictionary
        """
        model1 = self.get_model(model_group, version1)
        model2 = self.get_model(model_group, version2)
        
        if not model1 or not model2:
            return {}
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'metrics_comparison': {
                'accuracy': {
                    'v1': model1.metrics.get('accuracy'),
                    'v2': model2.metrics.get('accuracy'),
                    'diff': model2.metrics.get('accuracy', 0) - model1.metrics.get('accuracy', 0)
                },
                'f1_score': {
                    'v1': model1.metrics.get('f1_score'),
                    'v2': model2.metrics.get('f1_score'),
                    'diff': model2.metrics.get('f1_score', 0) - model1.metrics.get('f1_score', 0)
                }
            },
            'algorithm': {
                'v1': model1.algorithm,
                'v2': model2.algorithm
            },
            'created_at': {
                'v1': model1.created_at.isoformat(),
                'v2': model2.created_at.isoformat()
            }
        }
        
        return comparison
    
    def _generate_version(self, model_group: str) -> str:
        """Generate next version number."""
        versions = self.list_model_versions(model_group)
        if not versions:
            return "v1.0.0"
        
        # Parse latest version
        latest = versions[0].version
        parts = latest.replace('v', '').split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Increment patch version
        return f"v{major}.{minor}.{patch + 1}"
    
    def _save_metadata(self, metadata: ModelMetadata):
        """Save metadata to storage."""
        if self.use_dynamodb:
            self._save_to_dynamodb(metadata)
        else:
            self._save_to_filesystem(metadata)
    
    def _load_metadata(self, model_group: str, version: str) -> Optional[ModelMetadata]:
        """Load metadata from storage."""
        if self.use_dynamodb:
            return self._load_from_dynamodb(model_group, version)
        else:
            return self._load_from_filesystem(model_group, version)
    
    def _save_to_filesystem(self, metadata: ModelMetadata):
        """Save to local filesystem."""
        group_dir = os.path.join(self.registry_path, metadata.model_group)
        os.makedirs(group_dir, exist_ok=True)
        
        file_path = os.path.join(group_dir, f"{metadata.version}.json")
        
        with open(file_path, 'w') as f:
            json.dump({
                'model_group': metadata.model_group,
                'version': metadata.version,
                'algorithm': metadata.algorithm,
                'framework': metadata.framework,
                'framework_version': metadata.framework_version,
                'training_job_id': metadata.training_job_id,
                'dataset_version': metadata.dataset_version,
                'hyperparameters': metadata.hyperparameters,
                'metrics': metadata.metrics,
                'created_at': metadata.created_at.isoformat(),
                'created_by': metadata.created_by,
                'approval_status': metadata.approval_status.value,
                'tags': metadata.tags
            }, f, indent=2)
    
    def _load_from_filesystem(self, model_group: str, version: str) -> Optional[ModelMetadata]:
        """Load from local filesystem."""
        file_path = os.path.join(self.registry_path, model_group, f"{version}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return ModelMetadata(
            model_group=data['model_group'],
            version=data['version'],
            algorithm=data['algorithm'],
            framework=data['framework'],
            framework_version=data['framework_version'],
            training_job_id=data['training_job_id'],
            dataset_version=data['dataset_version'],
            hyperparameters=data['hyperparameters'],
            metrics=data['metrics'],
            created_at=datetime.fromisoformat(data['created_at']),
            created_by=data['created_by'],
            approval_status=ApprovalStatus(data['approval_status']),
            tags=data['tags']
        )
    
    def _list_from_filesystem(self, model_group: str) -> List[ModelMetadata]:
        """List versions from filesystem."""
        group_dir = os.path.join(self.registry_path, model_group)
        
        if not os.path.exists(group_dir):
            return []
        
        versions = []
        for filename in os.listdir(group_dir):
            if filename.endswith('.json'):
                version = filename.replace('.json', '')
                metadata = self._load_from_filesystem(model_group, version)
                if metadata:
                    versions.append(metadata)
        
        # Sort by created_at descending
        versions.sort(key=lambda x: x.created_at, reverse=True)
        return versions
    
    def _save_to_dynamodb(self, metadata: ModelMetadata):
        """Save to DynamoDB."""
        self.table.put_item(Item={
            'version': metadata.version,
            'model_group': metadata.model_group,
            'algorithm': metadata.algorithm,
            'framework': metadata.framework,
            'metrics': metadata.metrics,
            'created_at': metadata.created_at.isoformat(),
            'approval_status': metadata.approval_status.value
        })
    
    def _load_from_dynamodb(self, model_group: str, version: str) -> Optional[ModelMetadata]:
        """Load from DynamoDB."""
        response = self.table.get_item(Key={'version': version})
        if 'Item' not in response:
            return None
        
        item = response['Item']
        return ModelMetadata(
            model_group=item['model_group'],
            version=item['version'],
            algorithm=item['algorithm'],
            framework=item['framework'],
            framework_version=item.get('framework_version', '1.0'),
            training_job_id=item.get('training_job_id', ''),
            dataset_version=item.get('dataset_version', 'v1.0'),
            hyperparameters=item.get('hyperparameters', {}),
            metrics=item['metrics'],
            created_at=datetime.fromisoformat(item['created_at']),
            created_by=item.get('created_by', 'system'),
            approval_status=ApprovalStatus(item['approval_status']),
            tags=item.get('tags', {})
        )
    
    def _list_from_dynamodb(self, model_group: str) -> List[ModelMetadata]:
        """List versions from DynamoDB."""
        response = self.table.query(
            IndexName='ModelGroupIndex',
            KeyConditionExpression='model_group = :mg',
            ExpressionAttributeValues={':mg': model_group}
        )
        
        versions = []
        for item in response.get('Items', []):
            metadata = self._load_from_dynamodb(model_group, item['version'])
            if metadata:
                versions.append(metadata)
        
        versions.sort(key=lambda x: x.created_at, reverse=True)
        return versions
