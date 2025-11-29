"""
Data Drift Detection for MLOps Platform
Implements statistical drift detection algorithms
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from datetime import datetime

from src.models.data_models import DriftReport, Anomaly, StatisticsComparison, BaselineStatistics


class DriftDetector:
    """Detects data drift by comparing current data against baseline."""
    
    def __init__(self, baseline: BaselineStatistics, threshold: float = 0.1):
        """
        Initialize drift detector.
        
        Args:
            baseline: Baseline statistics
            threshold: Drift threshold (0-1)
        """
        self.baseline = baseline
        self.threshold = threshold
    
    def detect_drift(self, current_data: pd.DataFrame) -> DriftReport:
        """
        Detect drift in current data compared to baseline.
        
        Args:
            current_data: Current dataframe
            
        Returns:
            DriftReport object
        """
        drift_scores = {}
        features_with_drift = []
        anomalies = []
        stats_comparison = {}
        
        for feature_name, baseline_stats in self.baseline.feature_statistics.items():
            if feature_name not in current_data.columns:
                continue
            
            current_col = current_data[feature_name]
            
            # Calculate drift score
            drift_score = self._calculate_drift_score(current_col, baseline_stats)
            drift_scores[feature_name] = drift_score
            
            # Check if drift exceeds threshold
            if drift_score > self.threshold:
                features_with_drift.append(feature_name)
            
            # Create statistics comparison
            stats_comparison[feature_name] = StatisticsComparison(
                feature_name=feature_name,
                baseline_mean=baseline_stats.mean,
                current_mean=float(current_col.mean()) if np.issubdtype(current_col.dtype, np.number) else None,
                baseline_std=baseline_stats.std,
                current_std=float(current_col.std()) if np.issubdtype(current_col.dtype, np.number) else None,
                drift_score=drift_score
            )
            
            # Detect anomalies
            feature_anomalies = self._detect_anomalies(current_col, baseline_stats)
            anomalies.extend(feature_anomalies)
        
        # Calculate overall drift score
        overall_drift_score = np.mean(list(drift_scores.values())) if drift_scores else 0.0
        
        report = DriftReport(
            timestamp=datetime.now(),
            baseline_version=self.baseline.dataset_version,
            drift_score=float(overall_drift_score),
            features_with_drift=features_with_drift,
            anomalies=anomalies,
            statistics_comparison=stats_comparison
        )
        
        return report
    
    def _calculate_drift_score(self, current_col: pd.Series, baseline_stats) -> float:
        """
        Calculate drift score for a single feature.
        
        Uses different methods based on data type:
        - Numeric: Population Stability Index (PSI)
        - Categorical: Chi-square test
        """
        if np.issubdtype(current_col.dtype, np.number):
            return self._calculate_psi(current_col, baseline_stats)
        else:
            return self._calculate_chi_square(current_col, baseline_stats)
    
    def _calculate_psi(self, current_col: pd.Series, baseline_stats) -> float:
        """
        Calculate Population Stability Index (PSI) for numeric features.
        
        PSI = Σ (actual% - expected%) * ln(actual% / expected%)
        """
        if baseline_stats.mean is None or baseline_stats.std is None:
            return 0.0
        
        try:
            # Create bins based on baseline statistics
            baseline_mean = baseline_stats.mean
            baseline_std = baseline_stats.std
            
            bins = [
                baseline_mean - 2 * baseline_std,
                baseline_mean - baseline_std,
                baseline_mean,
                baseline_mean + baseline_std,
                baseline_mean + 2 * baseline_std
            ]
            
            # Expected distribution (normal)
            expected_pcts = [0.025, 0.135, 0.68, 0.135, 0.025]
            
            # Actual distribution
            current_binned = pd.cut(current_col, bins=bins, include_lowest=True)
            actual_counts = current_binned.value_counts(normalize=True, sort=False)
            actual_pcts = actual_counts.values
            
            # Calculate PSI
            psi = 0.0
            for actual, expected in zip(actual_pcts, expected_pcts):
                if actual > 0 and expected > 0:
                    psi += (actual - expected) * np.log(actual / expected)
            
            return abs(psi)
            
        except Exception:
            # Fallback to simple mean difference
            current_mean = current_col.mean()
            if baseline_stats.std > 0:
                return abs(current_mean - baseline_stats.mean) / baseline_stats.std
            return 0.0
    
    def _calculate_chi_square(self, current_col: pd.Series, baseline_stats) -> float:
        """Calculate chi-square statistic for categorical features."""
        try:
            # Get value counts
            current_counts = current_col.value_counts()
            
            # Assume uniform distribution as baseline
            expected_freq = len(current_col) / baseline_stats.unique_count
            expected_counts = pd.Series([expected_freq] * len(current_counts), index=current_counts.index)
            
            # Chi-square test
            chi2_stat, p_value = stats.chisquare(current_counts, expected_counts)
            
            # Normalize to 0-1 range
            return min(chi2_stat / 100, 1.0)
            
        except Exception:
            return 0.0
    
    def _detect_anomalies(self, current_col: pd.Series, baseline_stats) -> List[Anomaly]:
        """Detect anomalies in current data."""
        anomalies = []
        
        # Check for missing value spike
        missing_pct = (current_col.isnull().sum() / len(current_col)) * 100
        baseline_missing_pct = (baseline_stats.missing_count / 1000) * 100  # Assuming baseline size
        
        if missing_pct > baseline_missing_pct * 2 and missing_pct > 10:
            anomalies.append(Anomaly(
                feature_name=baseline_stats.feature_name,
                anomaly_type="missing_spike",
                severity="high" if missing_pct > 50 else "medium",
                description=f"Missing values increased from {baseline_missing_pct:.1f}% to {missing_pct:.1f}%"
            ))
        
        # Check for distribution shift (numeric only)
        if np.issubdtype(current_col.dtype, np.number) and baseline_stats.mean is not None:
            current_mean = current_col.mean()
            current_std = current_col.std()
            
            # Check if mean shifted significantly
            if baseline_stats.std > 0:
                z_score = abs(current_mean - baseline_stats.mean) / baseline_stats.std
                if z_score > 3:
                    anomalies.append(Anomaly(
                        feature_name=baseline_stats.feature_name,
                        anomaly_type="distribution_shift",
                        severity="high",
                        description=f"Mean shifted by {z_score:.2f} standard deviations"
                    ))
            
            # Check for outliers
            if baseline_stats.max is not None:
                outlier_count = ((current_col > baseline_stats.max * 1.5) | 
                               (current_col < baseline_stats.min * 0.5)).sum()
                outlier_pct = (outlier_count / len(current_col)) * 100
                
                if outlier_pct > 5:
                    anomalies.append(Anomaly(
                        feature_name=baseline_stats.feature_name,
                        anomaly_type="outliers",
                        severity="medium",
                        description=f"{outlier_pct:.1f}% of values are outliers"
                    ))
        
        return anomalies
    
    def publish_metrics(self, report: DriftReport) -> Dict[str, float]:
        """
        Publish drift metrics for monitoring.
        
        Args:
            report: DriftReport object
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'overall_drift_score': report.drift_score,
            'features_with_drift_count': len(report.features_with_drift),
            'anomaly_count': len(report.anomalies),
            'high_severity_anomalies': sum(1 for a in report.anomalies if a.severity == 'high')
        }
        
        return metrics
