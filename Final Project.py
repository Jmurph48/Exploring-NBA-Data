import pandas as pd


basic_2425 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA Basic 24-25.csv")
adv_2425 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA ADV 24-25.csv", header=1)
basic_2324 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA 2023-24 Basic.csv")
adv_2324 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA 2023-24 ADV.csv", header=1)
basic_2223 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA 2022-23 Basic.csv")
adv_2223 = pd.read_csv("C:/Users/jackm/OneDrive/Documents/Data Wrangling/NBA 2022-23 ADV.csv", header=1)

basic_2425["season"] = "2024-25"
adv_2425["season"]   = "2024-25"

basic_2324["season"] = "2023-24"
adv_2324["season"]   = "2023-24"

basic_2223["season"] = "2022-23"
adv_2223["season"]   = "2022-23"

basic_all = pd.concat([basic_2425, basic_2324, basic_2223], ignore_index=True)
adv_all   = pd.concat([adv_2425, adv_2324, adv_2223], ignore_index=True)

nba_all = pd.merge(basic_all, adv_all, on=["Team", "season"], how = 'left')
cols_to_drop = ["Rk_x", "Rk_y"]
cols_to_drop += [c for c in nba_all.columns if c.startswith("Unnamed:")]
nba_all = nba_all.drop(columns=cols_to_drop, errors='ignore')

nba_all["Team"] = nba_all["Team"].str.replace("*", "", regex=False).str.strip()
nba_all = nba_all[nba_all["Team"] != "League Average"]

nba_all = nba_all.reset_index(drop=True)

nba_all.columns


#Question 1: Which advanced stats explain winning the most in the NBA?

import seaborn as sns
import matplotlib.pyplot as plt

# Create win percentage
nba_all["win_pct"] = nba_all["W"] / nba_all["G"]

stats_to_test = [
    "ORtg", "DRtg", "NRtg", "efg_pct", "ts_pct",
    "tov_pct", "orb_pct", "FTr", "Pace"
]

corr_df = nba_all[["win_pct"] + stats_to_test].corr()

# Heatmap
plt.figure(figsize=(10, 7))
sns.heatmap(corr_df, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Between Advanced Stats and Winning")
plt.show()

# Correlation bar chart
win_corr = corr_df["win_pct"].drop("win_pct").sort_values()
win_corr.plot(kind="barh", figsize=(8,6), title="Correlation with Win Percentage")
plt.show()

#Question 2: Offense or Defense more important?

import numpy as np

print("Correlation with wins:")
print("ORtg:", nba_all["win_pct"].corr(nba_all["ORtg"]))
print("DRtg:", nba_all["win_pct"].corr(nba_all["DRtg"]))

import statsmodels.formula.api as smf

model = smf.ols("win_pct ~ ORtg + DRtg", data=nba_all).fit()
print(model.summary())

sns.scatterplot(data=nba_all, x="ORtg", y="win_pct")
sns.regplot(data=nba_all, x="ORtg", y="win_pct", scatter=False, color="red")
plt.title("Offensive Rating vs Win %")
plt.show()

sns.scatterplot(data=nba_all, x="DRtg", y="win_pct")
sns.regplot(data=nba_all, x="DRtg", y="win_pct", scatter=False, color="red")
plt.title("Defensive Rating vs Win %")
plt.show()

#Question 3: Improvement?

nba_all["season_num"] = nba_all["season"].astype(str).str[:4].astype(int)

nba_all = nba_all.sort_values(["Team", "season_num"])

nba_all["NRtg_change"] = nba_all.groupby("Team")["NRtg"].diff()

improvement = nba_all[nba_all["season"] == "2024-25"][["Team", "NRtg_change"]].dropna()
improvement = improvement.sort_values("NRtg_change", ascending=False)

print(improvement.head(10))

top_changes = improvement.head(10)

plt.figure(figsize=(14,8))
sns.barplot(data=top_changes, x="NRtg_change", y="Team", palette="viridis")
plt.title("Most Improved Teams in Net Rating (2023-24 → 2024-25)")
plt.xlabel("Change in Net Rating")
plt.ylabel("Team")
plt.show()
