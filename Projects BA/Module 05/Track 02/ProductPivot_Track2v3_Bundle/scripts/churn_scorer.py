#!/usr/bin/env python3
"""
PivotCo Product Pivot — Churn Probability Scorer (CLI Tool)

Trains a logistic regression model on customer features, scores every customer
with a churn probability, and emits the result as CSV ready for Power BI DAX
measures.

Usage:
    python churn_scorer.py --input data.csv --out outputs/
    python churn_scorer.py --input data.csv --out outputs/ --threshold 0.5

Outputs:
    churn_scores.csv          - one row per customer: customer_id, churn_prob, predicted_churn, segment
    model_diagnostics.txt     - AUC, confusion matrix, top coefficients
    feature_importance.csv    - logistic-regression coefficients (sorted)
"""
import argparse
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, classification_report,
                             confusion_matrix)


FEATURE_COLS_NUMERIC = ['tenure', 'MonthlyCharges', 'SeniorCitizen']
FEATURE_COLS_BINARY = ['Partner', 'Dependents', 'PhoneService', 'MultipleLines',
                       'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                       'TechSupport', 'StreamingTV', 'StreamingMovies',
                       'PaperlessBilling']
FEATURE_COLS_CATEGORICAL = ['Contract', 'PaymentMethod', 'InternetService']


def assign_segment(row):
    """Apply the same STP segmentation as the SQL view."""
    if row['tenure'] > 24 and row['MonthlyCharges'] > 70 and row['Contract'] != 'Month-to-month':
        return 'High Value Loyalists'
    if row['MonthlyCharges'] > 80 and row['Contract'] == 'Month-to-month':
        return 'At-Risk High Spenders'
    if row['features_adopted'] <= 1 and row['tenure'] < 12:
        return 'Low Engagement Newcomers'
    if row['tenure'] > 48 and row['Contract'] == 'Two year' and row['MonthlyCharges'] < 60:
        return 'Sticky Basics'
    return 'Mainstream'


def prepare_features(df):
    """Engineer features and create a model matrix."""
    df = df.copy()

    # Coerce TotalCharges
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

    # Features adopted
    feature_flags = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                     'TechSupport', 'StreamingTV', 'StreamingMovies']
    df['features_adopted'] = sum((df[f] == 'Yes').astype(int) for f in feature_flags)

    # Build model matrix
    X_num = df[FEATURE_COLS_NUMERIC].fillna(df[FEATURE_COLS_NUMERIC].median())
    X_num = X_num.copy()
    X_num['features_adopted'] = df['features_adopted']

    # Binary: handle "No internet/phone service" as "No"
    X_bin = pd.DataFrame()
    for col in FEATURE_COLS_BINARY:
        X_bin[col] = (df[col] == 'Yes').astype(int)

    # Categorical -> one-hot
    X_cat = pd.get_dummies(df[FEATURE_COLS_CATEGORICAL], drop_first=False).astype(int)

    X = pd.concat([X_num, X_bin, X_cat], axis=1)

    y = (df['Churn'] == 'Yes').astype(int) if 'Churn' in df.columns else None

    df['segment'] = df.apply(assign_segment, axis=1)

    return X, y, df


def train_and_score(df, out_dir):
    """Train logistic regression, score every customer, emit outputs."""
    X, y, df_enriched = prepare_features(df)

    print(f"Feature matrix: {X.shape}")
    print(f"Target balance: {y.mean():.3f} churn rate")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Train
    model = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    model.fit(X_train_s, y_train)

    # Test diagnostics
    y_pred = model.predict(X_test_s)
    y_pred_proba = model.predict_proba(X_test_s)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    diagnostics = []
    diagnostics.append("=" * 60)
    diagnostics.append("CHURN MODEL DIAGNOSTICS")
    diagnostics.append("=" * 60)
    diagnostics.append(f"\nTest set AUC: {auc:.4f}")
    diagnostics.append(f"Test set accuracy: {(y_pred == y_test).mean():.4f}")
    diagnostics.append(f"\nConfusion matrix:")
    cm = confusion_matrix(y_test, y_pred)
    diagnostics.append(f"  TN: {cm[0,0]:>5}    FP: {cm[0,1]:>5}")
    diagnostics.append(f"  FN: {cm[1,0]:>5}    TP: {cm[1,1]:>5}")
    diagnostics.append(f"\nClassification report:")
    diagnostics.append(classification_report(y_test, y_pred, target_names=['Stay', 'Churn']))

    # Feature importance
    coefs = pd.DataFrame({
        'feature': X.columns,
        'coefficient': model.coef_[0],
        'abs_coef': np.abs(model.coef_[0]),
    }).sort_values('abs_coef', ascending=False)

    diagnostics.append("\nTop 10 features by absolute coefficient:")
    for _, row in coefs.head(10).iterrows():
        direction = '+' if row['coefficient'] > 0 else '-'
        diagnostics.append(f"  [{direction}] {row['feature']:30s} coef={row['coefficient']:+.4f}")

    # Score everyone
    X_all_s = scaler.transform(X)
    df_enriched['churn_prob'] = model.predict_proba(X_all_s)[:, 1]
    df_enriched['predicted_churn'] = (df_enriched['churn_prob'] >= 0.5).astype(int)

    # Persist
    out_scores = df_enriched[['customerID', 'churn_prob', 'predicted_churn',
                              'segment', 'tenure', 'MonthlyCharges', 'Contract',
                              'features_adopted']].copy()
    out_scores.columns = ['customer_id', 'churn_prob', 'predicted_churn',
                          'segment', 'tenure_months', 'monthly_charges',
                          'contract_type', 'features_adopted']
    out_scores.to_csv(out_dir / 'churn_scores.csv', index=False)

    coefs.to_csv(out_dir / 'feature_importance.csv', index=False)
    (out_dir / 'model_diagnostics.txt').write_text('\n'.join(diagnostics))

    return auc, df_enriched


def main():
    parser = argparse.ArgumentParser(description='Churn probability scorer for SaaS subscribers')
    parser.add_argument('--input', '-i', required=True, help='Input CSV path')
    parser.add_argument('--out', '-o', default='./outputs', help='Output directory')
    parser.add_argument('--threshold', '-t', type=float, default=0.5,
                        help='Probability threshold for predicted_churn (default 0.5)')
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.input}...")
    df = pd.read_csv(args.input)
    print(f"  Loaded {len(df):,} customers")

    auc, df_scored = train_and_score(df, out_dir)

    print(f"\n=== Score distribution ===")
    print(df_scored['churn_prob'].describe().round(3).to_string())

    print(f"\n=== Score by segment ===")
    seg_summary = df_scored.groupby('segment').agg(
        n=('customerID', 'count'),
        avg_churn_prob=('churn_prob', 'mean'),
        actual_churn_rate=('Churn', lambda x: (x == 'Yes').mean()),
    ).round(3)
    print(seg_summary.to_string())

    print(f"\nDone. AUC={auc:.3f}. Outputs in {out_dir}")


if __name__ == '__main__':
    main()
