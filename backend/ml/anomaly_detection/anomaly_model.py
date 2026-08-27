import os

import joblib
from sklearn.ensemble import IsolationForest


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "anomaly_model.pkl"
)


class AnomalyDetectionModel:

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.05,
            random_state=42
        )

        self.is_trained = False

    def train(self, X):
        self.model.fit(X)

        self.is_trained = True

        self.save()

    def predict(self, X):
        if not self.is_trained:
            raise RuntimeError(
                "Anomaly model has not been trained."
            )

        return self.model.predict(X)

    def anomaly_score(self, X):
        if not self.is_trained:
            raise RuntimeError(
                "Anomaly model has not been trained."
            )

        return -self.model.score_samples(X)

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
