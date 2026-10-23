import pandas as pd
import numpy as np

np.random.seed(42)

districts = [
    "District_A",
    "District_B",
    "District_C",
    "District_D"
]

blocks = [
    "Block_1",
    "Block_2",
    "Block_3",
    "Block_4",
    "Block_5"
]

schemes = [
    "Food Support",
    "Housing Support",
    "Education Support",
    "Health Support"
]

rows = []

for i in range(1000):

    district = np.random.choice(districts)
    block = np.random.choice(blocks)
    scheme = np.random.choice(schemes)

    eligible = np.random.randint(100, 1000)

    coverage_rate = np.random.uniform(0.55, 0.95)

    received = int(eligible * coverage_rate)

    pending = np.random.randint(5, 150)

    processing_days = np.random.randint(2, 20)

    applications = received + pending + np.random.randint(10, 100)

    rejected = np.random.randint(0, 50)

    outreach = np.random.randint(10, 200)

    rows.append([
        district,
        block,
        scheme,
        eligible,
        received,
        pending,
        processing_days,
        applications,
        rejected,
        outreach
    ])


df = pd.DataFrame(
    rows,
    columns=[
        "district",
        "block",
        "scheme",
        "eligible",
        "received",
        "pending",
        "processing_days",
        "applications",
        "rejected",
        "outreach"
    ]
)

df.to_csv("data/welfare_data.csv", index=False)

print("Dataset created successfully!")
print(df.head())
