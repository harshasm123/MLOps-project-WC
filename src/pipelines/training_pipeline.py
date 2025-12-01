"""
SageMaker Training Pipeline for Medication Adherence Prediction
Supports multiple algorithms: RandomForest, XGBoost, LogisticRegression
"""

import boto3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb
import joblib
import json
import os
import argparse

def preprocess_data(df):
    """Preprocess medication adherence data."""
    # Handle categorical variables
    categorical_columns = ['gender', 'race', 'diagnosis', 'medication_type', 'dosage_frequency', 'insurance_type']
    
    for col in categorical_columns:
        if col in df.columns:
            df[col] = pd.Categorical(df[col]).codes
    
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    # Feature engineering
    if 'age' in df.columns and 'comorbidities_count' in df.columns:
        df['age_comorbidity_interaction'] = df['age'] * df['comorbidities_count']
    
    if 'previous_adherence_rate' in df.columns and 'num_medications' in df.columns:
        df['adherence_medication_ratio'] = df['previous_adherence_rate'] / (df['num_medications'] + 1)
    
    return df

def train_model(algorithm, X_train, y_train, hyperparameters=None):
    """Train model based on specified algorithm."""
    if hyperparameters is None:
        hyperparameters = {}
    
    if algorithm == 'RandomForest':
        model = RandomForestClassifier(
            n_estimators=hyperparameters.get('n_estimators', 100),
            max_depth=hyperparameters.get('max_depth', 10),
            min_samples_split=hyperparameters.get('min_samples_split', 2),
            random_state=42
        )
    elif algorithm == 'XGBoost':
        model = xgb.XGBClassifier(
            max_depth=hyperparameters.get('max_depth', 5),
            learning_rate=hyperparameters.get('eta', 0.2),
            n_estimators=hyperparameters.get('num_round', 100),
            objective='binary:logistic',
            random_state=42
        )
    elif algorithm == 'LogisticRegression':
        model = LogisticRegression(
            C=hyperparameters.get('C', 1.0),
            max_iter=hyperparameters.get('max_iter', 100),
            random_state=42
        )
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
        'auc_roc': roc_auc_score(y_test, y_pred_proba)
    }
    
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    parser.add_argument('--algorithm', type=str, default='RandomForest')
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    
    args = parser.parse_args()
    
    # Load data
    train_path = os.path.join(args.train, 'medication_adherence_sample.csv')
    df = pd.read_csv(train_path)
    
    print(f"Loaded {len(df)} samples with {len(df.columns)} features")
    
    # Preprocess data
    df = preprocess_data(df)
    
    # Prepare features and target
    target_column = 'adherence'
    feature_columns = [col for col in df.columns if col not in ['patient_id', target_column]]
    
    X = df[feature_columns]
    y = df[target_column]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    hyperparameters = {
        'n_estimators': args.n_estimators,
        'max_depth': args.max_depth
    }
    
    model = train_model(args.algorithm, X_train, y_train, hyperparameters)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    print("Model Performance:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Save model
    model_path = os.path.join(args.model_dir, 'model.joblib')
    joblib.dump(model, model_path)
    
    # Save feature names
    feature_names_path = os.path.join(args.model_dir, 'feature_names.json')
    with open(feature_names_path, 'w') as f:
        json.dump(feature_columns, f)
    
    # Save metrics
    metrics_path = os.path.join(args.model_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
    
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    main()