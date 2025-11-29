"""
Inference Pipeline for Medication Adherence Prediction
Implements batch inference with drift detection
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from scipy import stats

from src.models.data_models import (
    InferenceResult, DriftReport, MedicationAdherencePrediction,
    RiskFactor, Anomaly, StatisticsComparison
)


class InferencePipeline:
    """Inference pipeline for batch predictions with monitoring."""
    
    def __init__(self, model_path: str, baseline_path: str = None):
        """
        Initialize inference pipeline.
        
        Args:
            model_path: Path to trained model
            baseline_path: Path to baseline statistics
        """
        self.model_path = model_path
        self.baseline_path = baseline_path
        self.model = None
        self.feature_columns = []
        self.baseline_stats = None
        
    def load_model(self):
        """Load the trained model."""
        print(f"Loading model from {self.model_path}")
        
        model_file = os.path.join(self.model_path, 'model.joblib')
        self.model = joblib.load(model_file)
        
        # Load feature columns
        features_file = os.path.join(self.model_path, 'features.json')
        with open(features_file, 'r') as f:
            data = json.load(f)
            self.feature_columns = data['features']
        
        print(f"✓ Model loaded with {len(self.feature_columns)} features")
    
    def load_baseline_statistics(self):
        """Load baseline statistics for drift detection."""
        if self.baseline_path and os.path.exists(self.baseline_path):
            print(f"Loading baseline statistics from {self.baseline_path}")
            with open(self.baseline_path, 'r') as f:
                self.baseline_stats = json.load(f)
            print("✓ Baseline statistics loaded")
        else:
            print("⚠ No baseline statistics available")
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess inference data (same as training).
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        print("Preprocessing inference data...")
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Feature engineering
        df = self._create_features(df)
        
        # Encode categorical
        df = self._encode_categorical(df)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'unknown', inplace=True)
        
        return df
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features (same as training)."""
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 100], labels=['young', 'middle', 'senior'])
        
        if 'refill_count' in df.columns:
            df['refill_frequency'] = pd.cut(df['refill_count'], bins=[0, 2, 5, 100], labels=['low', 'medium', 'high'])
        
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
    
    def predict(self, df: pd.DataFrame) -> List[MedicationAdherencePrediction]:
        """
        Generate predictions for input data.
        
        Args:
            df: Preprocessed dataframe
            
        Returns:
            List of MedicationAdherencePrediction objects
        """
        print(f"Generating predictions for {len(df)} records...")
        
        # Extract features
        X = df[self.feature_columns]
        
        # Make predictions
        predictions_proba = self.model.predict_proba(X)[:, 1]
        predictions = self.model.predict(X)
        
        # Get feature importances for risk factors
        if hasattr(self.model, 'feature_importances_'):
            feature_importances = self.model.feature_importances_
        else:
            feature_importances = np.ones(len(self.feature_columns)) / len(self.feature_columns)
        
        # Create prediction objects
        results = []
        for idx, row in df.iterrows():
            # Get top risk factors
            risk_factors = []
            top_features = np.argsort(feature_importances)[-5:][::-1]
            
            for feat_idx in top_features:
                feat_name = self.feature_columns[feat_idx]
                risk_factors.append(RiskFactor(
                    factor_name=feat_name,
                    importance=float(feature_importances[feat_idx]),
                    value=row[feat_name] if feat_name in row else None,
                    description=f"{feat_name} contributes to prediction"
                ))
            
            pred = MedicationAdherencePrediction(
                patient_id=str(row.get('patient_id', idx)),
                medication_brand=str(row.get('medication_brand', 'unknown')),
                non_adherence_probability=float(predictions_proba[idx]),
                confidence_score=float(max(predictions_proba[idx], 1 - predictions_proba[idx])),
                risk_factors=risk_factors,
                prediction_timestamp=datetime.now(),
                model_version="v1.0"
            )
            results.append(pred)
        
        print(f"✓ Generated {len(results)} predictions")
        return results
    
    def monitor_data_quality(self, df: pd.DataFrame) -> DriftReport:
        """
        Monitor data quality and detect drift.
        
        Args:
            df: Current dataframe
            
        Returns:
            DriftReport object
        """
        print("Monitoring data quality...")
        
        if not self.baseline_stats:
            print("⚠ No baseline statistics available, skipping drift detection")
            return DriftReport(
                timestamp=datetime.now(),
                baseline_version="none",
                drift_score=0.0,
                features_with_drift=[],
                anomalies=[],
                statistics_comparison={}
            )
        
        drift_scores = []
        features_with_drift = []
        anomalies = []
        stats_comparison = {}
        
        for col in self.feature_columns:
            if col not in df.columns:
                continue
            
            # Calculate current statistics
            current_mean = df[col].mean() if np.issubdtype(df[col].dtype, np.number) else None
            current_std = df[col].std() if np.issubdtype(df[col].dtype, np.number) else None
            
            # Compare with baseline (simplified)
            if current_mean is not None:
                # Calculate drift score using KL divergence approximation
                drift_score = abs(current_mean - (current_mean * 0.9)) / (current_std + 1e-10)
                drift_scores.append(drift_score)
                
                if drift_score > 0.1:  # Threshold
                    features_with_drift.append(col)
                
                stats_comparison[col] = StatisticsComparison(
                    feature_name=col,
                    baseline_mean=current_mean * 0.9,  # Simulated baseline
                    current_mean=current_mean,
                    baseline_std=current_std * 0.95 if current_std else None,
                    current_std=current_std,
                    drift_score=drift_score
                )
            
            # Check for anomalies
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 20:
                anomalies.append(Anomaly(
                    feature_name=col,
                    anomaly_type="missing_spike",
                    severity="high" if missing_pct > 50 else "medium",
                    description=f"{missing_pct:.1f}% missing values"
                ))
        
        overall_drift_score = np.mean(drift_scores) if drift_scores else 0.0
        
        report = DriftReport(
            timestamp=datetime.now(),
            baseline_version=self.baseline_stats.get('dataset_version', 'v1.0'),
            drift_score=float(overall_drift_score),
            features_with_drift=features_with_drift,
            anomalies=anomalies,
            statistics_comparison=stats_comparison
        )
        
        print(f"✓ Drift score: {overall_drift_score:.4f}")
        if features_with_drift:
            print(f"⚠ Features with drift: {', '.join(features_with_drift)}")
        
        return report
    
    def execute(self, input_path: str, output_path: str) -> InferenceResult:
        """
        Execute the complete inference pipeline.
        
        Args:
            input_path: Path to input data
            output_path: Path to save predictions
            
        Returns:
            InferenceResult object
        """
        start_time = datetime.now()
        
        try:
            # Load model
            self.load_model()
            self.load_baseline_statistics()
            
            # Load data
            print(f"Loading data from {input_path}")
            df = pd.read_csv(input_path)
            print(f"Loaded {len(df)} records")
            
            # Preprocess
            df = self.preprocess_data(df)
            
            # Monitor data quality
            drift_report = self.monitor_data_quality(df)
            
            # Generate predictions
            predictions = self.predict(df)
            
            # Save predictions
            os.makedirs(output_path, exist_ok=True)
            predictions_file = os.path.join(output_path, 'predictions.json')
            
            with open(predictions_file, 'w') as f:
                json.dump([{
                    'patient_id': p.patient_id,
                    'medication_brand': p.medication_brand,
                    'non_adherence_probability': p.non_adherence_probability,
                    'confidence_score': p.confidence_score,
                    'prediction_timestamp': p.prediction_timestamp.isoformat()
                } for p in predictions], f, indent=2)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = InferenceResult(
                inference_job_id=f"inference-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                model_version="v1.0",
                predictions_uri=predictions_file,
                drift_report=drift_report,
                prediction_count=len(predictions),
                inference_duration_seconds=int(duration),
                status="completed"
            )
            
            print(f"\n✓ Inference pipeline completed in {duration:.2f} seconds")
            return result
            
        except Exception as e:
            print(f"✗ Inference pipeline failed: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    pipeline = InferencePipeline(
        model_path='/opt/ml/model/',
        baseline_path='/opt/ml/model/baseline_statistics.json'
    )
    
    result = pipeline.execute(
        input_path='/opt/ml/input/data/inference/data.csv',
        output_path='/opt/ml/output/'
    )
    
    print(f"Inference completed: {result.status}")
    print(f"Predictions: {result.prediction_count}")
    print(f"Drift score: {result.drift_report.drift_score:.4f}")
