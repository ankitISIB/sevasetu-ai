import pandas as pd

df = pd.read_csv("data/welfare_data.csv")

coordinates = {
    "Block_1": (23.8315, 91.2868),
    "Block_2": (23.8450, 91.3000),
    "Block_3": (23.8200, 91.3100),
    "Block_4": (23.8550, 91.2750),
    "Block_5": (23.8100, 91.2900)
}

df["latitude"] = df["block"].map(
    lambda x: coordinates[x][0]
)

df["longitude"] = df["block"].map(
    lambda x: coordinates[x][1]
)

df.to_csv(
    "data/welfare_data.csv",
    index=False
)

print("Coordinates added successfully.")
print(df.head())
