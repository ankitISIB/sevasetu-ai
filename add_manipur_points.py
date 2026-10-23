import pandas as pd

# Load existing Phase 1A dataset
df = pd.read_csv("data/welfare_data.csv")

# Synthetic demo locations across Manipur.
# These represent administrative analysis points,
# NOT real beneficiary locations.
manipur_points = [
    (24.8170, 93.9368),
    (24.7500, 94.0500),
    (24.6500, 94.1000),
    (24.5500, 93.8500),
    (24.4500, 93.7000),
    (24.9000, 94.2500),
    (25.0500, 94.3000),
    (24.9500, 93.7500),
    (24.3500, 93.9000),
    (24.6000, 94.3000),
]

# Give each existing synthetic district a Manipur location.
districts = df["district"].unique()

location_map = {}

for i, district in enumerate(districts):
    location_map[district] = manipur_points[i % len(manipur_points)]

# Add coordinates
df["latitude"] = df["district"].map(
    lambda x: location_map[x][0]
)

df["longitude"] = df["district"].map(
    lambda x: location_map[x][1]
)

# Save
df.to_csv(
    "data/welfare_data.csv",
    index=False
)

print("Manipur locations added successfully.")
print()

print(
    df[
        ["district", "block", "latitude", "longitude"]
    ].drop_duplicates().to_string(index=False)
)
