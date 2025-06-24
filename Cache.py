# Cache data for data analytics

import csv
import pandas as pd
import numpy as np
from tqdm import tqdm
from itertools import product
from datetime import datetime, timezone

# def load_binance_csv_files(file_paths):
#     candles = []
#     for path in file_paths:
#         with open(path, "r") as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 candles.append({
#                     "timestamp": int(row[0]) // 1000,
#                     "datetime": datetime.fromtimestamp(int(row[0]) // 1_000_000, timezone.utc),
#                     "open": float(row[1]),
#                     "high": float(row[2]),
#                     "low": float(row[3]),
#                     "close": float(row[4]),
#                     "volume": float(row[5]),
#                     "quote_volume": float(row[7]),
#                     "num_trades": int(row[8]),
#                     "taker_buy_base_vol": float(row[9]),
#                     "taker_buy_quote_vol": float(row[10]),
#                 })
#     candles.sort(key=lambda x: x["timestamp"])
#     df = pd.DataFrame(candles)
#     df.set_index('datetime', inplace=True)
#     return df
#
# # Load data
# files = [
#     'data/BTCUSDT-1m-2025-01.csv',
#     'data/BTCUSDT-1m-2025-02.csv',
#     'data/BTCUSDT-1m-2025-03.csv',
#     'data/BTCUSDT-1m-2025-04.csv',
#     'data/BTCUSDT-1m-2025-05.csv',
# ]
# df = load_binance_csv_files(files)
# df.to_pickle("data/full_data.pkl")

import pandas as pd
import numpy as np
from itertools import product
from tqdm import tqdm

# 1. Resample data to monthly close prices and compute monthly returns
df["return"] = np.log(df["close"] / df["close"].shift(1))

# Compute SMAs on full (minute-level) data
sma_windows = list(range(1, 301))
for win in sma_windows:
    df[f"sma_{win}"] = df["close"].rolling(window=win).mean()

# Save to pickle
df.to_pickle("data/full_data_with_smas.pkl")

# 2. Define SMA windows in months (for monthly data, windows from 1 to, say, 12)
sma_windows = list(range(1, 13))  # You can adjust max window

# 3. Precompute SMAs on monthly data
for win in sma_windows:
    df[f"sma_{win}"] = df["close"].rolling(window=win).mean()

results = []

sma_combinations = [(s, l) for s, l in product(sma_windows, sma_windows) if s < l]

for short_win, long_win in tqdm(sma_combinations, desc="Testing SMA pairs"):

    short_sma = monthly_df[f"sma_{short_win}"]
    long_sma = monthly_df[f"sma_{long_win}"]

    signal = np.where(short_sma > long_sma, 1, -1)
    shifted_signal = pd.Series(signal, index=monthly_df.index).shift(1)

    strategy_return = shifted_signal * monthly_df["return"]

    # Cumulative return over the entire period (log scale)
    cumulative_return = strategy_return.cumsum().iloc[-1]

    # Sharpe ratio (annualized, approx 12 months per year)
    sharpe = strategy_return.mean() / strategy_return.std() * np.sqrt(12)

    # Win rate = % of months where strategy return > 0
    win_rate = (strategy_return > 0).mean()

    results.append({
        "short": short_win,
        "long": long_win,
        "win_rate": win_rate,
        "cumulative_return": cumulative_return,
        "sharpe": sharpe,
    })

result_df = pd.DataFrame(results)

# Sort primarily by win rate (descending), then by cumulative_return and sharpe
result_df.sort_values(by=["win_rate", "cumulative_return", "sharpe"], ascending=False, inplace=True)

print(result_df.head(10))
