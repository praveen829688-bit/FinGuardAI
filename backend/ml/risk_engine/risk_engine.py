def calculate_rule_risk(
    amount_ratio: float,
    new_device: bool,
    unusual_location: bool,
    night_transaction: bool
):
    score = 0.0

    if amount_ratio >= 5:
        score += 30

    elif amount_ratio >= 3:
        score += 20

    elif amount_ratio >= 2:
        score += 10

    if new_device:
        score += 20

    if unusual_location:
        score += 20

    if night_transaction:
        score += 10

    return min(score, 100)


def calculate_final_risk(
    fraud_probability: float,
    anomaly_score: float,
    rule_score: float
):
    fraud_component = fraud_probability * 45

    anomaly_component = min(
        anomaly_score * 30,
        30
    )

    rule_component = rule_score * 0.25

    final_score = (
        fraud_component
        + anomaly_component
        + rule_component
    )

    return round(
        min(final_score, 100),
        2
    )


def risk_level(score: float):

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"
