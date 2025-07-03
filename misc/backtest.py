import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from analytics.MOMENTUM import (
    sma_crossover_strategy,
    roc_crossover_strategy,
    ema_crossover_strategy,
    macd_crossover_strategy,
    rsi_crossover_strategy,
    bollinger_band_strategy,
    momentum_volume_strategy,
)
from tqdm import tqdm

# === Load and preprocess data ===
df = pd.read_pickle("../data/misc/full_data.pkl")
df.dropna(inplace=True)
print(df.index)
df["return"] = np.log(df["close"] / df["close"].shift(1))
df.dropna(inplace=True)


# === Time split ===
in_sample = df[df.index < "2025-05-01"]
out_sample = df[df.index >= "2025-05-01"]

# === Strategy list ===
strategies = [
    sma_crossover_strategy,
    ema_crossover_strategy,
    roc_crossover_strategy,
    macd_crossover_strategy,
    rsi_crossover_strategy,
    bollinger_band_strategy,
    momentum_volume_strategy
]

# === Aggregated signal function ===
def aggregated_signal(candles, threshold=0.7):
    buy_votes = sum(1 for strat in strategies if strat(candles).get("signal") == "buy")
    sell_votes = sum(1 for strat in strategies if strat(candles).get("signal") == "sell")
    total = len(strategies)

    if buy_votes / total >= threshold:
        return "buy"
    elif sell_votes / total >= threshold:
        return "sell"
    return "hold"

# === Backtest core ===
def run_backtest(data, threshold=0.7, window=300):
    position = 0
    returns = []

    for i in tqdm(range(window, len(data) - 1), desc="Backtesting"):
        candles = data.iloc[i - window:i].to_dict("records")
        signal = aggregated_signal(candles, threshold)
        next_ret = data["return"].iloc[i + 1]

        if signal == "buy" and position <= 0:
            position = 1
        elif signal == "sell" and position >= 0:
            position = -1

        returns.append(position * next_ret)

    return pd.Series(returns, index=data.index[window + 1:])

# === Performance metrics ===
def performance_metrics(returns):
    cumulative = (returns + 1).cumprod()
    total_return = cumulative.iloc[-1] - 1
    sharpe = returns.mean() / returns.std() * np.sqrt(60 * 24)
    max_dd = (cumulative / cumulative.cummax() - 1).min()
    return {
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": max_dd
    }

# === Run backtests ===
final_in = run_backtest(in_sample)
final_out = run_backtest(out_sample)

in_metrics = performance_metrics(final_in)
out_metrics = performance_metrics(final_out)

# === Print results ===
print("\n=== In-Sample Metrics ===")
for k, v in in_metrics.items():
    print(f"{k}: {v:.4f}")

print("\n=== Out-of-Sample Metrics ===")
for k, v in out_metrics.items():
    print(f"{k}: {v:.4f}")

# === Plot equity curves ===
plt.figure(figsize=(12, 6))
plt.plot((final_in + 1).cumprod(), label="In-Sample")
plt.plot((final_out + 1).cumprod(), label="Out-of-Sample")
plt.title("Equity Curve - In vs Out of Sample")
plt.xlabel("Time")
plt.ylabel("Equity Growth")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
