# cache_full_data.py
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timezone

def load_binance_csv_files(file_paths):
    candles = []
    for path in file_paths:
        with open(path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                candles.append({
                    "timestamp": int(row[0]) // 1000,
                    "datetime": datetime.fromtimestamp(int(row[0]) // 1_000_000, timezone.utc),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                    "quote_volume": float(row[7]),
                    "num_trades": int(row[8]),
                    "taker_buy_base_vol": float(row[9]),
                    "taker_buy_quote_vol": float(row[10]),
                })
    candles.sort(key=lambda x: x["timestamp"])
    df = pd.DataFrame(candles)
    df.set_index('datetime', inplace=True)
    return df

# Load data
files = [
    'data/BTCUSDT-1m-2025-01.csv',
    'data/BTCUSDT-1m-2025-02.csv',
    'data/BTCUSDT-1m-2025-03.csv',
    'data/BTCUSDT-1m-2025-04.csv',
    'data/BTCUSDT-1m-2025-05.csv',
]
df = load_binance_csv_files(files)
df["return"] = np.log(df["close"] / df["close"].shift(1))

df.to_pickle("data/full_data.pkl")