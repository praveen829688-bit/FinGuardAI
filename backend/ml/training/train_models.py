import os

import joblib
import pandas as pd

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "transactions.csv"
)

FRAUD_MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "fraud_detection",
    "fraud_model.pkl"
)

ANOMALY_MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "anomaly_detection",
    "anomaly_model.pkl"
)


df = pd.read_csv(DATA_PATH)

features = [
    "amount",
    "amount_ratio",
    "new_device",
    "unusual_location",
    "night_transaction",
    "transaction_type"
]

X = df[features]
y = df["fraud"]


categorical_features = [
    "transaction_type"
]

numeric_features = [
    "amount",
    "amount_ratio",
    "new_device",
    "unusual_location",
    "night_transaction"
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


fraud_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=15,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


print("\nTraining Random Forest fraud model...")

fraud_pipeline.fit(
    X_train,
    y_train
)


predictions = fraud_pipeline.predict(
    X_test
)

probabilities = fraud_pipeline.predict_proba(
    X_test
)[:, 1]


print("\n===== FRAUD MODEL PERFORMANCE =====")

print(
    f"Accuracy : "
    f"{accuracy_score(y_test, predictions):.4f}"
)

print(
    f"Precision: "
    f"{precision_score(y_test, predictions):.4f}"
)

print(
    f"Recall   : "
    f"{recall_score(y_test, predictions):.4f}"
)

print(
    f"F1 Score : "
    f"{f1_score(y_test, predictions):.4f}"
)

print(
    f"ROC-AUC  : "
    f"{roc_auc_score(y_test, probabilities):.4f}"
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)

print("Confusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions
    )
)


joblib.dump(
    fraud_pipeline,
    FRAUD_MODEL_PATH
)

print(
    f"\nFraud model saved to:\n"
    f"{FRAUD_MODEL_PATH}"
)


print("\nTraining Isolation Forest anomaly model...")

X_anomaly = X.copy()

X_anomaly = pd.get_dummies(
    X_anomaly,
    columns=["transaction_type"]
)

anomaly_model = IsolationForest(
    n_estimators=300,
    contamination=0.05,
    random_state=42
)

anomaly_model.fit(
    X_anomaly
)

joblib.dump(
    {
        "model": anomaly_model,
        "columns": list(X_anomaly.columns)
    },
    ANOMALY_MODEL_PATH
)

print(
    f"Anomaly model saved to:\n"
    f"{ANOMALY_MODEL_PATH}"
)

print("\nAI model training completed successfully.")
