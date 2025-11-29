"""
Training Pipeline for Medication Adherence Prediction
Implements the complete training workflow for SageMaker
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import xgboost as xgb
import joblib
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple

from src.models.data_models import EvaluationMetrics, TrainingResult, BaselineStatistics, FeatureStats


class TrainingPipeline:
    """Main training pipeline for medication adherence prediction."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize training pipeline.
        
        Args:
            config: Configuration dictionary with hyperparameters and settings
        """
        self.config = config
        self.algorithm = config.get('algorithm', 'RandomForest')
        self.model = None
        self.feature_columns = []
        
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Load training data from CSV."""
        print(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preprocess data for training.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Tuple of (train_df, test_df)
        """
        print("Preprocessing data...")
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Feature engineering
        df = self._create_features(df)
        
        # Encode categorical variables
        df = self._encode_categorical(df)
        
        # Split into train and test
        train_df, test_df = train_test_split(
            df, 
            test_size=0.2, 
            random_state=42,
            stratify=df['non_adherence'] if 'non_adherence' in df.columns else None
        )
        
        print(f"Training set: {len(train_df)} rows")
        print(f"Test set: {len(test_df)} rows")
        
        return train_df, test_df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical columns with mode
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].mode()[0], inplace=True)
        
        return df
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create additional features for the model."""
        # Age groups
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 100], labels=['young', 'middle', 'senior'])
        
        # Refill frequency
        if 'refill_count' in df.columns:
            df['refill_frequency'] = pd.cut(df['refill_count'], bins=[0, 2, 5, 100], labels=['low', 'medium', 'high'])
        
        # Days since prescription (if date column exists)
        if 'prescription_date' in df.columns:
            df['prescription_date'] = pd.to_datetime(df['prescription_date'])
            df['days_since_prescription'] = (pd.Timestamp.now() - df['prescription_date']).dt.days
        
        return df
    
    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables."""
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_columns:
            if col not in ['patient_id', 'prescription_date']:
                df[col] = pd.Categorical(df[col]).codes
        
        return df
    
    def train_model(self, train_df: pd.DataFrame) -> Any:
        """
        Train the ML model.
        
        Args:
            train_df: Training dataframe
            
        Returns:
            Trained model
        """
        print(f"Training {self.algorithm} model...")
        
        # Separate features and target
        target_col = 'non_adherence'
        exclude_cols = ['patient_id', 'prescription_date', target_col]
        
        self.feature_columns = [col for col in train_df.columns if col not in exclude_cols]
        
        X_train = train_df[self.feature_columns]
        y_train = train_df[target_col] if target_col in train_df.columns else None
        
        # Initialize model based on algorithm
        if self.algorithm == 'RandomForest':
            self.model = RandomForestClassifier(
                n_estimators=self.config.get('n_estimators', 100),
                max_depth=self.config.get('max_depth', 10),
                random_state=42,
                n_jobs=-1
            )
        elif self.algorithm == 'XGBoost':
            self.model = xgb.XGBClassifier(
                max_depth=self.config.get('max_depth', 5),
                learning_rate=self.config.get('learning_rate', 0.1),
                n_estimators=self.config.get('n_estimators', 100),
                random_state=42
            )
        elif self.algorithm == 'LogisticRegression':
            self.model = LogisticRegression(
                C=self.config.get('C', 1.0),
                max_iter=self.config.get('max_iter', 1000),
                random_state=42
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Train model
        self.model.fit(X_train, y_train)
        
        print(f"✓ Model training complete")
        return self.model
    
    def evaluate_model(self, test_df: pd.DataFrame) -> EvaluationMetrics:
        """
        Evaluate the trained model.
        
        Args:
            test_df: Test dataframe
            
        Returns:
            EvaluationMetrics object
        """
        print("Evaluating model...")
        
        target_col = 'non_adherence'
        X_test = test_df[self.feature_columns]
        y_test = test_df[target_col]
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = EvaluationMetrics(
            accuracy=accuracy_score(y_test, y_pred),
            precision=precision_score(y_test, y_pred, zero_division=0),
            recall=recall_score(y_test, y_pred, zero_division=0),
            f1_score=f1_score(y_test, y_pred, zero_division=0),
            auc_roc=roc_auc_score(y_test, y_pred_proba),
            confusion_matrix=confusion_matrix(y_test, y_pred).tolist()
        )
        
        print(f"Accuracy: {metrics.accuracy:.4f}")
        print(f"Precision: {metrics.precision:.4f}")
        print(f"Recall: {metrics.recall:.4f}")
        print(f"F1 Score: {metrics.f1_score:.4f}")
        print(f"AUC-ROC: {metrics.auc_roc:.4f}")
        
        return metrics
    
    def create_baseline_statistics(self, train_df: pd.DataFrame) -> BaselineStatistics:
        """
        Create baseline statistics for data quality monitoring.
        
        Args:
            train_df: Training dataframe
            
        Returns:
            BaselineStatistics object
        """
        print("Creating baseline statistics...")
        
        feature_stats = {}
        
        for col in self.feature_columns:
            if col in train_df.columns:
                stats = FeatureStats(
                    feature_name=col,
                    data_type=str(train_df[col].dtype),
                    mean=float(train_df[col].mean()) if np.issubdtype(train_df[col].dtype, np.number) else None,
                    std=float(train_df[col].std()) if np.issubdtype(train_df[col].dtype, np.number) else None,
                    min=float(train_df[col].min()) if np.issubdtype(train_df[col].dtype, np.number) else None,
                    max=float(train_df[col].max()) if np.issubdtype(train_df[col].dtype, np.number) else None,
                    missing_count=int(train_df[col].isnull().sum()),
                    unique_count=int(train_df[col].nunique())
                )
                feature_stats[col] = stats
        
        baseline = BaselineStatistics(
            dataset_version="v1.0",
            created_at=datetime.now(),
            feature_statistics=feature_stats
        )
        
        print(f"✓ Baseline statistics created for {len(feature_stats)} features")
        return baseline
    
    def save_model(self, output_path: str):
        """Save the trained model."""
        print(f"Saving model to {output_path}")
        
        os.makedirs(output_path, exist_ok=True)
        
        # Save model
        model_file = os.path.join(output_path, 'model.joblib')
        joblib.dump(self.model, model_file)
        
        # Save feature columns
        features_file = os.path.join(output_path, 'features.json')
        with open(features_file, 'w') as f:
            json.dump({'features': self.feature_columns}, f)
        
        print(f"✓ Model saved successfully")
    
    def execute(self, data_path: str, output_path: str) -> TrainingResult:
        """
        Execute the complete training pipeline.
        
        Args:
            data_path: Path to training data
            output_path: Path to save model and artifacts
            
        Returns:
            TrainingResult object
        """
        start_time = datetime.now()
        
        try:
            # Load data
            df = self.load_data(data_path)
            
            # Preprocess
            train_df, test_df = self.preprocess_data(df)
            
            # Train
            self.train_model(train_df)
            
            # Evaluate
            metrics = self.evaluate_model(test_df)
            
            # Create baseline
            baseline = self.create_baseline_statistics(train_df)
            
            # Save model
            self.save_model(output_path)
            
            # Save baseline
            baseline_file = os.path.join(output_path, 'baseline_statistics.json')
            with open(baseline_file, 'w') as f:
                json.dump({
                    'dataset_version': baseline.dataset_version,
                    'created_at': baseline.created_at.isoformat(),
                    'feature_count': len(baseline.feature_statistics)
                }, f)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = TrainingResult(
                model_version="v1.0",
                training_job_id=f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                metrics=metrics,
                model_artifact_uri=output_path,
                baseline_statistics_uri=baseline_file,
                training_duration_seconds=int(duration),
                status="completed"
            )
            
            print(f"\n✓ Training pipeline completed in {duration:.2f} seconds")
            return result
            
        except Exception as e:
            print(f"✗ Training pipeline failed: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    config = {
        'algorithm': 'RandomForest',
        'n_estimators': 100,
        'max_depth': 10
    }
    
    pipeline = TrainingPipeline(config)
    result = pipeline.execute(
        data_path='/opt/ml/input/data/training/train.csv',
        output_path='/opt/ml/model/'
    )
    
    print(f"Training completed: {result.status}")
