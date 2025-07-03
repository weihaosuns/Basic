import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm
from scipy.stats import ttest_1samp

DATA_PATH = "../data/misc/full_data.pkl"

with open(DATA_PATH, "rb") as f:
    cached = pickle.load(f)
price_df = cached["close"]
return_df = cached["return"]
return_df = return_df.to_frame(name="return")
return_df = return_df.sort_index()
return_df["month"] = return_df.index.to_period("M")

months = return_df["month"].sort_values().unique()
in_sample_months = months[:len(months)-1]
out_sample_month = months[-1]

test_return_df = return_df[return_df["month"].isin(in_sample_months)]
train_return_df = return_df[return_df["month"] == out_sample_month]

# # Precompute SMA
# sma_windows = list(range(1, 301, 1))
# sma_dict = {}
# for win in sma_windows:
#     sma_dict[f"sma_{win}"] = price_df.rolling(window=win).mean()
#
# sma_df = pd.DataFrame(sma_dict, index=price_df.index)
# sma_df.to_pickle("data/sma_data.pkl")


# sma_windows = list(range(1, 101, 1))
# SMA_PATH = "data/sma_data.pkl"
# with open(SMA_PATH, "rb") as f:
#     cached = pickle.load(f)
# sma_df = cached
# sma_df = sma_df.sort_index()
# sma_df["month"] = sma_df.index.to_period("M")
#
# test_sma_df = sma_df[sma_df["month"].isin(in_sample_months)]
# train_sma_df = sma_df[sma_df["month"] == out_sample_month]
#
# sma_combinations = [(s, l) for s in sma_windows for l in sma_windows if s < l]
#
# results = []
# pnl_matrix = []
#
# for short_win, long_win in tqdm(sma_combinations, desc="Testing SMA pairs"):
#     short_sma = test_sma_df[f"sma_{short_win}"]
#     long_sma = test_sma_df[f"sma_{long_win}"]
#
#     signal = np.where(short_sma > long_sma, 1, -1).astype(float)
#     shifted_signal = pd.Series(signal, index=test_sma_df.index).shift(1)
#
#     valid_idx = shifted_signal.dropna().index
#     strat_df = pd.DataFrame({
#         "signal": shifted_signal.loc[valid_idx],
#         "return": test_return_df.loc[valid_idx, "return"]
#     })
#
#     strat_df["strategy_return"] = strat_df["signal"] * strat_df["return"]
#     if strat_df["strategy_return"].std() == 0 or len(strat_df) < 10:
#         continue
#
#     mean_return = strat_df["strategy_return"].mean()
#     std_return = strat_df["strategy_return"].std()
#     t_stat, p_value = ttest_1samp(strat_df["strategy_return"], popmean=0, alternative='greater')
#
#     results.append({
#         "short": short_win,
#         "long": long_win,
#         "mean_return": mean_return,
#         "std_return": std_return,
#         "t_stat": t_stat,
#         "p_value": p_value,
#     })
#
#     # Collect strategy PnL vector for White's RC
#     pnl_matrix.append(strat_df["strategy_return"].values)
#
# # Results as DataFrame
# result_df = pd.DataFrame(results)
#
# def bhy_procedure(p_values, alpha=0.05):
#     m = len(p_values)
#     sorted_idx = np.argsort(p_values)
#     sorted_pvals = np.array(p_values)[sorted_idx]
#     c_m = np.sum(1 / np.arange(1, m + 1))  # harmonic number
#     thresholds = np.arange(1, m + 1) * alpha / (m * c_m)
#
#     # Find the largest p where p <= threshold
#     is_significant = sorted_pvals <= thresholds
#     max_k = np.where(is_significant)[0].max() if is_significant.any() else -1
#
#     mask = np.zeros(m, dtype=bool)
#     if max_k >= 0:
#         mask[sorted_idx[:max_k + 1]] = True
#     return mask
#
# result_df["bhy_pass"] = bhy_procedure(result_df["p_value"].values, alpha=0.05)
#
# significant_strats = result_df[result_df["bhy_pass"]]
# result_df.to_pickle("data/sma_results.pkl")
#
# min_len = min(len(p) for p in pnl_matrix)
# pnl_matrix_trimmed = np.array([p[:min_len] for p in pnl_matrix])  # shape (num_strategies, min_len)
#
# # Save to file
# with open("data/sma_pnl_matrix.pkl", "wb") as f:
#     pickle.dump(pnl_matrix_trimmed, f)

SMA_RESULTS_PATH = "../data/misc/sma_results.pkl"
with open(SMA_RESULTS_PATH, "rb") as f:
    cached = pickle.load(f)
sma_results_df = cached

print(sma_results_df["bhy_pass"].unique())
# for m in sma_results_df["month"].unique():
#     print(f"-------------- Win Ratio for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("win_ratio", ascending=False).head(10))
#     print(f"-------------- Cumulative Return for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("cumulative_return", ascending=False).head(10))
#     print(f"-------------- Sharpe Ratio for {m} --------------")
#     print(sma_results_df[sma_results_df["month"] == m].sort_values("sharpe", ascending=False).head(10))