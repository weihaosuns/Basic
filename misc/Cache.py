# Cache data for data analytics

import csv
import pandas as pd
import numpy as np
import os
import pickle
from tqdm import tqdm
from itertools import product
from datetime import datetime, timezone

DATA_PATH = "../data/misc/full_data.pkl"

with open(DATA_PATH, "rb") as f:
    cached = pickle.load(f)
price_df = cached["close"]
return_df = cached["return"]
return_df = return_df.to_frame(name="return")
return_df = return_df.sort_index()
return_df["month"] = return_df.index.to_period("M")

#################
##    SMA      ##
#################

sma_windows = list(range(1, 301, 1))
# sma_dict = {}
# for win in sma_windows:
#     sma_dict[f"sma_{win}"] = price_df.rolling(window=win).mean()
#
# sma_df = pd.DataFrame(sma_dict, index=price_df.index)
# sma_df.to_pickle("data/sma_data.pkl")
sma_windows = list(range(1, 301, 1))
SMA_PATH = "../data/misc/sma_data.pkl"
with open(SMA_PATH, "rb") as f:
    cached = pickle.load(f)
sma_df = cached
sma_df = sma_df.sort_index()

results = []

sma_combinations = [(s, l) for s in sma_windows for l in sma_windows if s < l]

for short_win, long_win in tqdm(sma_combinations, desc="Testing SMA pairs"):
    short_sma = sma_df[f"sma_{short_win}"]
    long_sma = sma_df[f"sma_{long_win}"]

    signal = np.where(short_sma > long_sma, 1, -1).astype(float)
    shifted_signal = pd.Series(signal, index=sma_df.index).shift(1)

    strat_df = pd.DataFrame({
        "signal": shifted_signal,
        "return": return_df["return"],
        "month": return_df["month"]
    })

    strat_df = strat_df.dropna()

    monthly_group = strat_df.groupby("month")

    for month, group in monthly_group:

        strategy_return = group["signal"] * group["return"]
        cumulative_return = strategy_return.cumsum().iloc[-1]
        sharpe = strategy_return.mean() / strategy_return.std() * np.sqrt(1440) if strategy_return.std() > 0 else 0
        win_ratio = (strategy_return > 0).mean()
        num_trades = group["signal"].diff().fillna(0).ne(0).sum()

        results.append({
            "short": short_win,
            "long": long_win,
            "month": str(month),
            "monthly_return": strategy_return.sum(),
            "cumulative_return": cumulative_return,
            "sharpe": sharpe,
            "win_ratio": win_ratio,
            "num_trades": int(num_trades)
        })

sma_results_df = pd.DataFrame(results)
sma_results_df.to_pickle("data/sma_results.pkl")

# SMA_RESULTS_PATH = "data/sma_results.pkl"
# with open(SMA_RESULTS_PATH, "rb") as f:
#     cached = pickle.load(f)
# sma_results_df = cached
# for m in sma_results_df["month"].unique():
#     print(f"-------------- Win Ratio for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("win_ratio", ascending=False).head(10))
#     print(f"-------------- Cumulative Return for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("cumulative_return", ascending=False).head(10))
#     print(f"-------------- Sharpe Ratio for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("sharpe", ascending=False).head(10))

#################
##    ROC      ##
#################

roc_windows = list(range(1, 301, 1))
# roc_dict = {}
#
# for win in roc_windows:
#     roc_dict[f"roc_{win}"] = price_df.pct_change(periods=win)
# roc_df = pd.DataFrame(roc_dict, index=price_df.index)
# roc_df.to_pickle("data/roc_data.pkl")

ROC_PATH = "../data/misc/roc_data.pkl"
with open(ROC_PATH, "rb") as f:
    cached = pickle.load(f)
roc_df = cached
roc_df = roc_df.sort_index()

results = []

roc_combinations = [(s, l) for s, l in product(roc_windows, roc_windows) if s < l]

for short_win, long_win in tqdm(roc_combinations, desc="Testing ROC pairs"):
    short_roc = roc_df[f"roc_{short_win}"]
    long_roc = roc_df[f"roc_{long_win}"]

    signal = np.where(short_roc > long_roc, 1, -1).astype(float)
    shifted_signal = pd.Series(signal, index=roc_df.index).shift(1)

    strat_df = pd.DataFrame({
        "signal": shifted_signal,
        "return": return_df["return"],
        "month": return_df["month"]
    })

    strat_df = strat_df.dropna()

    monthly_group = strat_df.groupby("month")

    for month, group in monthly_group:

        strategy_return = group["signal"] * group["return"]
        cumulative_return = strategy_return.cumsum().iloc[-1]
        sharpe = strategy_return.mean() / strategy_return.std() * np.sqrt(1440) if strategy_return.std() > 0 else 0
        win_ratio = (strategy_return > 0).mean()
        num_trades = group["signal"].diff().fillna(0).ne(0).sum()

        results.append({
            "short": short_win,
            "long": long_win,
            "month": str(month),
            "monthly_return": strategy_return.sum(),
            "cumulative_return": cumulative_return,
            "sharpe": sharpe,
            "win_ratio": win_ratio,
            "num_trades": int(num_trades)
        })

roc_results_df = pd.DataFrame(results)
roc_results_df.to_pickle("data/roc_results.pkl")

# ROC_RESULTS_PATH = "data/roc_results.pkl"
# with open(ROC_RESULTS_PATH, "rb") as f:
#     cached = pickle.load(f)
# roc_results_df = cached
# for m in roc_results_df["month"].unique():
#     print(f"-------------- Win Ratio for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("win_ratio", ascending=False).head(10))
#     print(f"-------------- Cumulative Return for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("cumulative_return", ascending=False).head(10))
#     print(f"-------------- Sharpe Ratio for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("sharpe", ascending=False).head(10))

#################
##    EMA      ##
#################

ema_windows = list(range(1, 301, 1))
# ema_dict = {}
#
# for win in ema_windows:
#     ema_dict[f"ema_{win}"] = price_df.ewm(span=win, adjust=False).mean()
# ema_df = pd.DataFrame(ema_dict, index=price_df.index)
# ema_df.to_pickle("data/ema_data.pkl")

EMA_PATH = "../data/misc/ema_data.pkl"
with open(EMA_PATH, "rb") as f:
    cached = pickle.load(f)
ema_df = cached
ema_df = ema_df.sort_index()

results = []

ema_combinations = [(s, l) for s, l in product(ema_windows, ema_windows) if s < l]

for short_win, long_win in tqdm(ema_combinations, desc="Testing EMA pairs"):
    short_ema = ema_df[f"ema_{short_win}"]
    long_ema = ema_df[f"ema_{long_win}"]

    signal = np.where(short_ema > long_ema, 1, -1).astype(float)
    shifted_signal = pd.Series(signal, index=ema_df.index).shift(1)

    strat_df = pd.DataFrame({
        "signal": shifted_signal,
        "return": return_df["return"],
        "month": return_df["month"]
    })

    strat_df = strat_df.dropna()

    monthly_group = strat_df.groupby("month")

    for month, group in monthly_group:

        strategy_return = group["signal"] * group["return"]
        cumulative_return = strategy_return.cumsum().iloc[-1]
        sharpe = strategy_return.mean() / strategy_return.std() * np.sqrt(1440) if strategy_return.std() > 0 else 0
        win_ratio = (strategy_return > 0).mean()
        num_trades = group["signal"].diff().fillna(0).ne(0).sum()

        results.append({
            "short": short_win,
            "long": long_win,
            "month": str(month),
            "monthly_return": strategy_return.sum(),
            "cumulative_return": cumulative_return,
            "sharpe": sharpe,
            "win_ratio": win_ratio,
            "num_trades": int(num_trades)
        })

roc_results_df = pd.DataFrame(results)
roc_results_df.to_pickle("data/roc_results.pkl")

# ROC_RESULTS_PATH = "data/roc_results.pkl"
# with open(ROC_RESULTS_PATH, "rb") as f:
#     cached = pickle.load(f)
# roc_results_df = cached
# for m in roc_results_df["month"].unique():
#     print(f"-------------- Win Ratio for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("win_ratio", ascending=False).head(10))
#     print(f"-------------- Cumulative Return for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("cumulative_return", ascending=False).head(10))
#     print(f"-------------- Sharpe Ratio for {m} --------------")
#     print(roc_results_df[roc_results_df["month"] == m].sort_values("sharpe", ascending=False).head(10))