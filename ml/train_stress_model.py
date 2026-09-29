"""Training & Model Selection Script for Repayment Stress Classification.

Trains and evaluates:
- Random Forest Classifier
- Logistic Regression (with StandardScaler)

Computes Accuracy, Precision, Recall, F1-score, and Confusion Matrix.
Saves the best classification model to ml/models/stress_classifier.joblib.
"""
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from data_preprocessing import create_stress_dataset
from model_evaluation import evaluate_classification

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_select_stress_model():
    print("=== STEP 5: REPAYMENT STRESS CLASSIFIER TRAINING ===")
    df, feature_cols, target_col = create_stress_dataset()
    print(f"Total dataset samples: {len(df)}")
    print(f"Feature columns ({len(feature_cols)}): {feature_cols}")

    # Temporal split: dates <= 2026-02-28 for training, remainder for test
    split_date = pd.to_datetime("2026-02-28")
    train_mask = df["date"] <= split_date
    test_mask = df["date"] > split_date

    X_train = df.loc[train_mask, feature_cols]
    y_train = df.loc[train_mask, target_col]

    X_test = df.loc[test_mask, feature_cols]
    y_test = df.loc[test_mask, target_col]

    labels = ["LOW", "MEDIUM", "HIGH"]
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Class distribution in test set:\n{y_test.value_counts()}")

    # -------------------------------------------------------------
    # 1. Logistic Regression (with StandardScaler)
    # -------------------------------------------------------------
    print("\n--- Training Logistic Regression ---")
    lr_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    lr_pipeline.fit(X_train, y_train)
    lr_preds = lr_pipeline.predict(X_test)
    lr_metrics = evaluate_classification(y_test, lr_preds, labels=labels)
    print(f"Logistic Regression Metrics: Acc={lr_metrics['accuracy']}, F1_macro={lr_metrics['f1_macro']}, F1_weighted={lr_metrics['f1_weighted']}")

    # -------------------------------------------------------------
    # 2. Random Forest Classifier
    # -------------------------------------------------------------
    print("\n--- Training Random Forest Classifier ---")
    rf_clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_clf.fit(X_train, y_train)
    rf_preds = rf_clf.predict(X_test)
    rf_metrics = evaluate_classification(y_test, rf_preds, labels=labels)
    print(f"Random Forest Metrics:      Acc={rf_metrics['accuracy']}, F1_macro={rf_metrics['f1_macro']}, F1_weighted={rf_metrics['f1_weighted']}")

    # Model Selection based on F1-macro
    if rf_metrics["f1_macro"] >= lr_metrics["f1_macro"]:
        best_model = rf_clf
        best_name = "RandomForestClassifier"
        best_metrics = rf_metrics
    else:
        best_model = lr_pipeline
        best_name = "LogisticRegression"
        best_metrics = lr_metrics

    print(f"\nSelected Best Stress Classifier: {best_name} (F1_macro={best_metrics['f1_macro']}, Accuracy={best_metrics['accuracy']})")

    # -------------------------------------------------------------
    # 3. Save Model Artifact & Metadata
    # -------------------------------------------------------------
    model_path = MODELS_DIR / "stress_classifier.joblib"
    joblib.dump(best_model, model_path)

    metadata = {
        "feature_cols": feature_cols,
        "selected_model": best_name,
        "labels": labels,
        "metrics": best_metrics,
        "comparisons": {
            "LogisticRegression": {
                "accuracy": lr_metrics["accuracy"],
                "precision_macro": lr_metrics["precision_macro"],
                "recall_macro": lr_metrics["recall_macro"],
                "f1_macro": lr_metrics["f1_macro"],
                "f1_weighted": lr_metrics["f1_weighted"],
                "confusion_matrix": lr_metrics["confusion_matrix"],
            },
            "RandomForestClassifier": {
                "accuracy": rf_metrics["accuracy"],
                "precision_macro": rf_metrics["precision_macro"],
                "recall_macro": rf_metrics["recall_macro"],
                "f1_macro": rf_metrics["f1_macro"],
                "f1_weighted": rf_metrics["f1_weighted"],
                "confusion_matrix": rf_metrics["confusion_matrix"],
            },
        },
    }

    with open(MODELS_DIR / "stress_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved stress model and metadata to {MODELS_DIR}")
    return metadata


if __name__ == "__main__":
    train_and_select_stress_model()
