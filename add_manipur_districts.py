import pandas as pd
import numpy as np

INPUT_FILE = "data/welfare_data.csv"
OUTPUT_FILE = "data/welfare_data.csv"

# ============================================================
# LOAD EXISTING DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

# ============================================================
# 16 SYNTHETIC MANIPUR LOCATIONS
# ============================================================
#
# IMPORTANT:
# These are DEMO coordinates for the prototype.
# They do NOT represent real beneficiaries.
#

manipur_locations = {
    "Area-01": (24.8170, 93.9368),
    "Area-02": (24.7500, 94.0500),
    "Area-03": (24.6500, 94.1000),
    "Area-04": (24.5500, 93.8500),
    "Area-05": (24.4500, 93.7000),
    "Area-06": (24.9000, 94.2500),
    "Area-07": (25.0500, 94.3000),
    "Area-08": (24.9500, 93.7500),
    "Area-09": (24.3500, 93.9000),
    "Area-10": (24.6000, 94.3000),
    "Area-11": (24.3000, 94.1500),
    "Area-12": (24.8500, 93.6500),
    "Area-13": (25.1500, 94.0500),
    "Area-14": (24.4000, 94.4000),
    "Area-15": (24.7000, 93.5500),
    "Area-16": (25.0000, 93.9500),
}

areas = list(manipur_locations.keys())

# ============================================================
# MAKE SURE WE HAVE 16 ROWS
# ============================================================

if len(df) < 16:

    additional_rows = 16 - len(df)

    extra = df.sample(
        n=additional_rows,
        replace=True,
        random_state=42
    )

    df = pd.concat(
        [df, extra],
        ignore_index=True
    )

# Keep exactly 16 rows for this prototype map
df = df.iloc[:16].copy()

# Reset index so .loc[i] works correctly
df = df.reset_index(drop=True)

# ============================================================
# FORCE NUMERIC COLUMNS TO FLOAT
# ============================================================
#
# This prevents the Pandas int64 / decimal-value error.
#

numeric_columns = [
    "eligible",
    "received",
    "applications",
    "pending",
    "rejected",
    "outreach",
    "processing_days",
    "latitude",
    "longitude",
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).astype(float)

# ============================================================
# ASSIGN SYNTHETIC AREA NAMES
# ============================================================

df["district"] = areas

# ============================================================
# ASSIGN BLOCK NAMES
# ============================================================

block_names = [
    "North Block",
    "Central Block",
    "South Block",
]

df["block"] = [
    block_names[i % len(block_names)]
    for i in range(len(df))
]

# ============================================================
# RISK PROFILES
# ============================================================
#
# These profiles intentionally create different welfare
# conditions so the AI dashboard demonstrates:
#
# 🔴 Critical
# 🟠 High
# 🟡 Medium
# 🟢 Normal
#
# This is synthetic demonstration data.
#

risk_profiles = {

    "Area-01": "critical",
    "Area-02": "normal",
    "Area-03": "high",
    "Area-04": "critical",

    "Area-05": "medium",
    "Area-06": "normal",
    "Area-07": "high",
    "Area-08": "critical",

    "Area-09": "medium",
    "Area-10": "normal",
    "Area-11": "high",
    "Area-12": "medium",

    "Area-13": "critical",
    "Area-14": "normal",
    "Area-15": "high",
    "Area-16": "medium",
}

# Reproducible random generator
rng = np.random.default_rng(42)

# ============================================================
# GENERATE SYNTHETIC WELFARE CONDITIONS
# ============================================================

for i, area in enumerate(areas):

    profile = risk_profiles[area]

    # --------------------------------------------------------
    # CRITICAL
    # --------------------------------------------------------

    if profile == "critical":

        eligible = rng.integers(900, 1400)

        received = int(
            eligible * rng.uniform(0.30, 0.48)
        )

        applications = rng.integers(600, 900)

        pending = int(
            applications * rng.uniform(0.28, 0.40)
        )

        rejected = int(
            applications * rng.uniform(0.12, 0.20)
        )

        processing_days = rng.uniform(18, 30)

        outreach = rng.integers(20, 60)

    # --------------------------------------------------------
    # HIGH
    # --------------------------------------------------------

    elif profile == "high":

        eligible = rng.integers(850, 1300)

        received = int(
            eligible * rng.uniform(0.45, 0.62)
        )

        applications = rng.integers(550, 850)

        pending = int(
            applications * rng.uniform(0.18, 0.28)
        )

        rejected = int(
            applications * rng.uniform(0.08, 0.14)
        )

        processing_days = rng.uniform(12, 20)

        outreach = rng.integers(40, 90)

    # --------------------------------------------------------
    # MEDIUM
    # --------------------------------------------------------

    elif profile == "medium":

        eligible = rng.integers(800, 1200)

        received = int(
            eligible * rng.uniform(0.58, 0.72)
        )

        applications = rng.integers(500, 800)

        pending = int(
            applications * rng.uniform(0.10, 0.18)
        )

        rejected = int(
            applications * rng.uniform(0.05, 0.10)
        )

        processing_days = rng.uniform(7, 14)

        outreach = rng.integers(60, 120)

    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    else:

        eligible = rng.integers(750, 1100)

        received = int(
            eligible * rng.uniform(0.75, 0.92)
        )

        applications = rng.integers(450, 750)

        pending = int(
            applications * rng.uniform(0.03, 0.09)
        )

        rejected = int(
            applications * rng.uniform(0.02, 0.06)
        )

        processing_days = rng.uniform(3, 8)

        outreach = rng.integers(90, 160)

    # ========================================================
    # SAVE GENERATED VALUES
    # ========================================================

    df.loc[i, "eligible"] = float(eligible)

    df.loc[i, "received"] = float(received)

    df.loc[i, "applications"] = float(applications)

    df.loc[i, "pending"] = float(pending)

    df.loc[i, "rejected"] = float(rejected)

    df.loc[i, "processing_days"] = float(
        round(processing_days, 1)
    )

    df.loc[i, "outreach"] = float(outreach)

    # ========================================================
    # MANIPUR COORDINATES
    # ========================================================

    df.loc[i, "latitude"] = float(
        manipur_locations[area][0]
    )

    df.loc[i, "longitude"] = float(
        manipur_locations[area][1]
    )

# ============================================================
# FINAL DATA CLEANUP
# ============================================================

# Convert count columns back to integers
integer_columns = [
    "eligible",
    "received",
    "applications",
    "pending",
    "rejected",
    "outreach",
]

for column in integer_columns:

    if column in df.columns:

        df[column] = (
            pd.to_numeric(
                df[column],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

# Keep processing days as decimal
df["processing_days"] = (
    pd.to_numeric(
        df["processing_days"],
        errors="coerce"
    )
    .round(1)
)

# Coordinates as decimals
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# ============================================================
# SAVE DATA
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("=" * 70)
print("MANIPUR SYNTHETIC WELFARE DATA CREATED SUCCESSFULLY")
print("=" * 70)
print()

print(
    df[
        [
            "district",
            "block",
            "eligible",
            "received",
            "pending",
            "rejected",
            "processing_days",
            "latitude",
            "longitude",
        ]
    ].to_string(index=False)
)

print()
print("=" * 70)
print("AREAS CREATED:", len(df))
print("=" * 70)
print()

print("Risk distribution:")

for risk in ["critical", "high", "medium", "normal"]:

    count = list(risk_profiles.values()).count(risk)

    print(
        f"  {risk.upper():8} : {count}"
    )

print()
print("Saved to:")
print(OUTPUT_FILE)

print()
print("IMPORTANT:")
print("This dataset is SYNTHETIC demo data.")
print("Coordinates do NOT represent real beneficiaries.")
print("=" * 70)
