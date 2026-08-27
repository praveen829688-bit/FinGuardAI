import os

import joblib
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
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


class FinGuardRiskService:

    def __init__(self):
        self.fraud_model = joblib.load(
            FRAUD_MODEL_PATH
        )

        anomaly_data = joblib.load(
            ANOMALY_MODEL_PATH
        )

        self.anomaly_model = anomaly_data["model"]
        self.anomaly_columns = anomaly_data["columns"]

    def analyze(
        self,
        amount: float,
        amount_ratio: float,
        new_device: bool,
        unusual_location: bool,
        night_transaction: bool,
        transaction_type: str
    ):
        data = pd.DataFrame([{
            "amount": amount,
            "amount_ratio": amount_ratio,
            "new_device": int(new_device),
            "unusual_location": int(unusual_location),
            "night_transaction": int(night_transaction),
            "transaction_type": transaction_type
        }])

        fraud_probability = float(
            self.fraud_model.predict_proba(data)[0][1]
        )

        anomaly_input = pd.get_dummies(
            data,
            columns=["transaction_type"]
        )

        anomaly_input = anomaly_input.reindex(
            columns=self.anomaly_columns,
            fill_value=0
        )

        anomaly_raw = float(
            -self.anomaly_model.score_samples(
                anomaly_input
            )[0]
        )

        anomaly_score = min(
            anomaly_raw * 30,
            30
        )

        rule_score = 0.0
        reasons = []

        if amount_ratio >= 5:
            rule_score += 30
            reasons.append(
                "Transaction amount is significantly above normal spending."
            )
        elif amount_ratio >= 3:
            rule_score += 20
            reasons.append(
                "Transaction amount is unusually high."
            )
        elif amount_ratio >= 2:
            rule_score += 10
            reasons.append(
                "Transaction amount is above normal spending."
            )

        if new_device:
            rule_score += 20
            reasons.append(
                "Transaction originated from a new device."
            )

        if unusual_location:
            rule_score += 20
            reasons.append(
                "Transaction location is unusual."
            )

        if night_transaction:
            rule_score += 10
            reasons.append(
                "Transaction occurred during unusual hours."
            )

        final_score = (
            fraud_probability * 45
            + anomaly_score
            + rule_score * 0.25
        )

        final_score = round(
            min(final_score, 100),
            2
        )

        if final_score >= 80:
            status = "CRITICAL"
        elif final_score >= 60:
            status = "HIGH_RISK"
        elif final_score >= 30:
            status = "MEDIUM_RISK"
        else:
            status = "LOW_RISK"

        if not reasons:
            reasons.append(
                "No significant behavioral risk indicators detected."
            )

        return {
            "fraud_probability": round(
                fraud_probability * 100,
                2
            ),
            "anomaly_score": round(
                anomaly_score,
                2
            ),
            "rule_score": round(
                rule_score,
                2
            ),
            "risk_score": final_score,
            "status": status,
            "reasons": reasons
        }


risk_service = FinGuardRiskService()
