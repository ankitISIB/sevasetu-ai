from sklearn.ensemble import IsolationForest


def detect_anomalies(df):

    features = [
        "coverage_gap",
        "pending_rate",
        "rejection_rate",
        "processing_days"
    ]

    X = df[features]

    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    df = df.copy()

    predictions = model.fit_predict(X)

    df["anomaly"] = predictions

    df["anomaly_status"] = df["anomaly"].apply(
        lambda x: "Unusual" if x == -1 else "Normal"
    )

    return df, model
