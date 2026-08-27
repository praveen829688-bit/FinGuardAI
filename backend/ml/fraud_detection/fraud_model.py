import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "fraud_model.pkl"
)


class FraudDetectionModel:

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            class_weight="balanced"
        )

        self.is_trained = False

    def train(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True
        self.save()

    def predict_probability(self, X):
        if not self.is_trained:
            raise RuntimeError(
                "Fraud model has not been trained."
            )

        return self.model.predict_proba(X)[:, 1]

    def save(self):
        joblib.dump(
            self.model,
            MODEL_PATH
        )

    def load(self):
        if not os.path.exists(MODEL_PATH):
            return False

        self.model = joblib.load(
            MODEL_PATH
        )

        self.is_trained = True

        return True
