import os

import numpy as np
import pandas as pd


OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "datasets",
    "transactions.csv"
)

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)

rng = np.random.default_rng(42)

ROWS = 10000

amount = rng.lognormal(
    mean=7.0,
    sigma=1.0,
    size=ROWS
)

amount_ratio = rng.lognormal(
    mean=0.0,
    sigma=0.7,
    size=ROWS
)

new_device = rng.binomial(
    1,
    0.12,
    ROWS
)

unusual_location = rng.binomial(
    1,
    0.10,
    ROWS
)

night_transaction = rng.binomial(
    1,
    0.15,
    ROWS
)

transaction_types = rng.choice(
    ["PAYMENT", "TRANSFER", "WITHDRAWAL", "DEPOSIT"],
    size=ROWS,
    p=[0.55, 0.25, 0.15, 0.05]
)

risk_signal = (
    (amount_ratio > 4).astype(int)
    + (new_device * 2)
    + (unusual_location * 2)
    + night_transaction
    + (transaction_types == "TRANSFER").astype(int)
)

fraud_probability = 1 / (
    1 + np.exp(
        -(risk_signal - 3.2)
    )
)

fraud = (
    rng.random(ROWS) < fraud_probability
).astype(int)

df = pd.DataFrame({
    "amount": amount,
    "amount_ratio": amount_ratio,
    "new_device": new_device,
    "unusual_location": unusual_location,
    "night_transaction": night_transaction,
    "transaction_type": transaction_types,
    "fraud": fraud
})

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"Created development dataset: {OUTPUT_PATH}"
)

print(f"Rows: {len(df)}")
print(
    "Fraud cases:",
    int(df["fraud"].sum())
)
print(
    "Legitimate cases:",
    int((df["fraud"] == 0).sum())
)
