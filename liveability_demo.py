"""Composite Liveability Index (CLI) demo on SYNTHETIC data.
Author: Aung Kaung Myat (MSc GIS & Remote Sensing, University College Dublin)

Shows the index method used in my Dublin Small Area project: four indicators are normalised to 0-1,
averaged into one score and classified into five classes with Natural Breaks (Jenks).
The data here is made up (400 areas on a grid), so no downloads are needed.
"""
import mapclassify as mc
import numpy as np
import pandas as pd

SEED, SIDE = 42, 20


def make_synthetic_areas():
    """Areas on a grid: services are more likely near the centre, green space towards the edge."""
    rng = np.random.default_rng(SEED)
    x, y = np.meshgrid(np.arange(SIDE), np.arange(SIDE))
    df = pd.DataFrame({"x": x.ravel(), "y": y.ravel()})
    centre = 1 - np.hypot(df["x"] - SIDE / 2, df["y"] - SIDE / 2) / (SIDE / 2 * 1.42)  # 1 = centre, 0 = edge
    df["has_health_500m"] = (rng.random(len(df)) < 0.2 + 0.7 * centre).astype(int)
    df["has_transit_400m"] = (rng.random(len(df)) < 0.2 + 0.7 * centre).astype(int)
    df["green_space_ratio"] = np.clip(rng.normal(0.15 + 0.35 * (1 - centre), 0.08), 0, 1)
    df["active_travel_density"] = rng.gamma(2.0, 1.5 + 2 * centre)  # km of paths per km2
    return df


df = make_synthetic_areas()

# 1. Normalise: continuous indicators divided by their maximum, binary indicators stay 0 / 1
df["CLI"] = pd.concat([
    df["green_space_ratio"] / df["green_space_ratio"].max(),
    df["active_travel_density"] / df["active_travel_density"].max(),
    df["has_transit_400m"],
    df["has_health_500m"],
], axis=1).mean(axis=1)

# 2. Five classes using Natural Breaks (Jenks)
labels = ["Very Low", "Low", "Medium", "High", "Very High"]
jenks = mc.FisherJenks(df["CLI"].values, k=5)
df["CLI_class"] = pd.Categorical.from_codes(jenks.yb, labels, ordered=True)

# 3. Summary
print("Class breaks:", [round(float(b), 3) for b in jenks.bins])
print(df["CLI_class"].value_counts().sort_index())
df.to_csv("liveability_demo_results.csv", index=False)
