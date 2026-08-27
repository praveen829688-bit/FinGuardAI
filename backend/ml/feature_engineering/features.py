from datetime import datetime


def transaction_features(
    amount: float,
    transaction_type: str,
    has_new_device: bool,
    unusual_location: bool,
    previous_average: float,
    hour: int | None = None
):
    if hour is None:
        hour = datetime.now().hour

    amount_ratio = (
        amount / previous_average
        if previous_average > 0
        else 1.0
    )

    night_transaction = (
        1 if hour < 6 or hour >= 23 else 0
    )

    return {
        "amount": amount,
        "amount_ratio": amount_ratio,
        "new_device": int(has_new_device),
        "unusual_location": int(unusual_location),
        "night_transaction": night_transaction,
        "transaction_type": transaction_type
    }
