"""Formula 1 historical data analysis (1950-2024).

Original FastF1 setup by Umer Farooq (cache configuration below);
historical analysis completed from the Ergast-style CSV dataset in data/.
Run:  python src/f1_analysis.py
Outputs land in outputs/: driver wins/points tables + 2 charts.
"""
import os
try:
    import fastf1
except ImportError:
    fastf1 = None  # optional: only needed for live FastF1 session work
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Original FastF1 cache setup ---
cache_folder = 'cache_folder'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)
if fastf1 is not None:
    fastf1.Cache.enable_cache(cache_folder)

# --- Historical analysis ---
BASE = os.path.join(os.path.dirname(__file__), "..")
drivers = pd.read_csv(os.path.join(BASE, "data", "drivers.csv"))
races = pd.read_csv(os.path.join(BASE, "data", "races.csv"))
results = pd.read_csv(os.path.join(BASE, "data", "results.csv"), na_values="\\N")
os.makedirs(os.path.join(BASE, "outputs"), exist_ok=True)

wins = (results[results.positionOrder == 1]
        .merge(drivers, on="driverId")
        .groupby(["forename", "surname"]).size()
        .sort_values(ascending=False).rename("wins").reset_index())
wins.to_csv(os.path.join(BASE, "outputs", "top_drivers_by_wins.csv"), index=False)

points = (results.groupby("driverId")["points"].sum()
          .sort_values(ascending=False).rename("points").reset_index()
          .merge(drivers, on="driverId"))
points[["forename", "surname", "points"]].head(20).to_csv(
    os.path.join(BASE, "outputs", "top_drivers_by_points.csv"), index=False)

fig, ax = plt.subplots(figsize=(9, 5))
top = wins.head(10).iloc[::-1]
ax.barh(top.forename + " " + top.surname, top.wins)
ax.set_xlabel("Career wins"); ax.set_title("Top 10 drivers by wins, 1950-2024")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "outputs", "top10_wins.png"), dpi=150)

races_per_decade = races.assign(decade=(races.year // 10) * 10).groupby("decade").size()
fig, ax = plt.subplots(figsize=(9, 4))
races_per_decade.plot(kind="bar", ax=ax)
ax.set_ylabel("Races"); ax.set_title("F1 races per decade, 1950-2024")
fig.tight_layout(); fig.savefig(os.path.join(BASE, "outputs", "races_per_decade.png"), dpi=150)

print(wins.head(5)); print("Done - outputs in outputs/")
