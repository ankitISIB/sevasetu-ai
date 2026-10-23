def calculate_priority_score(df):

    df = df.copy()

    gap_score = df["coverage_gap"].clip(0, 100)

    pending_score = (
        df["pending_rate"]
        .clip(0, 100)
    )

    delay_score = (
        df["processing_days"]
        .clip(0, 30)
        / 30
    ) * 100

    rejection_score = (
        df["rejection_rate"]
        .clip(0, 100)
    )

    df["priority_score"] = (
        0.40 * gap_score +
        0.25 * pending_score +
        0.20 * delay_score +
        0.15 * rejection_score
    )

    df["priority_score"] = (
        df["priority_score"]
        .clip(0, 100)
        .round(2)
    )

    return df

