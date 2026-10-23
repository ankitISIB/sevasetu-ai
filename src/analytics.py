import pandas as pd


def calculate_metrics(df):

    df = df.copy()

    df["coverage"] = (
        df["received"] / df["eligible"]
    ) * 100

    df["coverage"] = df["coverage"].clip(0, 100)

    df["coverage_gap"] = 100 - df["coverage"]

    df["pending_rate"] = (
        df["pending"] / df["applications"]
    ) * 100

    df["rejection_rate"] = (
        df["rejected"] / df["applications"]
    ) * 100

    return df


def area_summary(df):

    summary = df.groupby(
        ["district", "block"]
    ).agg(
        eligible=("eligible", "sum"),
        received=("received", "sum"),
        pending=("pending", "sum"),
        applications=("applications", "sum"),
        rejected=("rejected", "sum"),
        outreach=("outreach", "sum"),
        processing_days=("processing_days", "mean")
    ).reset_index()

    summary["coverage"] = (
        summary["received"] /
        summary["eligible"]
    ) * 100

    summary["coverage_gap"] = (
        100 - summary["coverage"]
    )

    summary["pending_rate"] = (
        summary["pending"] /
        summary["applications"]
    ) * 100

    summary["rejection_rate"] = (
        summary["rejected"] /
        summary["applications"]
    ) * 100

    return summary

import pandas as pd


def calculate_metrics(df):

    df = df.copy()

    df["coverage"] = (
        df["received"] /
        df["eligible"]
    ) * 100

    df["coverage"] = df["coverage"].clip(0, 100)

    df["coverage_gap"] = (
        100 - df["coverage"]
    )

    df["pending_rate"] = (
        df["pending"] /
        df["applications"]
    ) * 100

    df["rejection_rate"] = (
        df["rejected"] /
        df["applications"]
    ) * 100

    return df


def area_summary(df):

    summary = df.groupby(
        ["district", "block"]
    ).agg(
        eligible=("eligible", "sum"),
        received=("received", "sum"),
        pending=("pending", "sum"),
        applications=("applications", "sum"),
        rejected=("rejected", "sum"),
        outreach=("outreach", "sum"),
        processing_days=("processing_days", "mean"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first")
    ).reset_index()

    summary["coverage"] = (
        summary["received"] /
        summary["eligible"]
    ) * 100

    summary["coverage"] = summary[
        "coverage"
    ].clip(0, 100)

    summary["coverage_gap"] = (
        100 - summary["coverage"]
    )

    summary["pending_rate"] = (
        summary["pending"] /
        summary["applications"]
    ) * 100

    summary["rejection_rate"] = (
        summary["rejected"] /
        summary["applications"]
    ) * 100

    return summary
