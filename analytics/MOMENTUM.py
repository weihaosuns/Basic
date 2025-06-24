import numpy as np
import pandas as pd

def sma_crossover_strategy(candles, short_window=1, long_window=3):
    if len(candles) < long_window + 1:
        return {"signal": "hold"}

    closes = np.array([c["close"] for c in candles])

    short_sma = closes[-short_window:].mean()
    long_sma = closes[-long_window:].mean()
    prev_short_sma = closes[-short_window-1:-1].mean()
    prev_long_sma = closes[-long_window-1:-1].mean()

    if prev_short_sma <= prev_long_sma and short_sma > long_sma:
        return {"signal": "buy"}
    elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}


def roc_crossover_strategy(candles, short_window=2, long_window=9):
    if len(candles) < long_window + 1:
        return {"signal": "hold"}

    closes = np.array([c["close"] for c in candles])

    short_roc = (closes[-1] - closes[-1 - short_window]) / closes[-1 - short_window]
    long_roc = (closes[-1] - closes[-1 - long_window]) / closes[-1 - long_window]

    prev_short_roc = (closes[-2] - closes[-2 - short_window]) / closes[-2 - short_window]
    prev_long_roc = (closes[-2] - closes[-2 - long_window]) / closes[-2 - long_window]

    if prev_short_roc <= prev_long_roc and short_roc > long_roc:
        return {"signal": "buy"}
    elif prev_short_roc >= prev_long_roc and short_roc < long_roc:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}

def ema_crossover_strategy(candles, short_window=1, long_window=3):
    if len(candles) < long_window + 2:  # need 2 extra for prev EMA
        return {"signal": "hold"}

    closes = pd.Series([c["close"] for c in candles])

    def compute_ema(series, span):
        return series.ewm(span=span, adjust=False).mean().iloc[-1]

    short_ema = compute_ema(closes, short_window)
    long_ema = compute_ema(closes, long_window)
    prev_short_ema = compute_ema(closes[:-1], short_window)
    prev_long_ema = compute_ema(closes[:-1], long_window)

    if prev_short_ema <= prev_long_ema and short_ema > long_ema:
        return {"signal": "buy"}
    elif prev_short_ema >= prev_long_ema and short_ema < long_ema:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}

def macd_crossover_strategy(candles, fast=1, slow=5, signal_len=5):
    if len(candles) < slow + signal_len + 1:
        return {"signal": "hold"}

    closes = pd.Series([c["close"] for c in candles])

    ema_fast = closes.ewm(span=fast, adjust=False).mean()
    ema_slow = closes.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_len, adjust=False).mean()

    curr_macd = macd_line.iloc[-1]
    curr_signal = signal_line.iloc[-1]
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]

    if prev_macd <= prev_signal and curr_macd > curr_signal:
        return {"signal": "buy"}
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}

def rsi_crossover_strategy(candles, short_window=2, long_window=21):
    if len(candles) < long_window + 2:
        return {"signal": "hold"}

    closes = pd.Series([c["close"] for c in candles])
    delta = closes.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    def compute_rsi(series_gain, series_loss, span):
        avg_gain = series_gain.ewm(span=span, adjust=False).mean()
        avg_loss = series_loss.ewm(span=span, adjust=False).mean()
        rs = avg_gain / avg_loss
        rs = rs.replace([np.inf, -np.inf], np.nan).fillna(0)
        return 100 - (100 / (1 + rs))

    rsi_short = compute_rsi(gain, loss, short_window)
    rsi_long = compute_rsi(gain, loss, long_window)

    curr_short = rsi_short.iloc[-1]
    curr_long = rsi_long.iloc[-1]
    prev_short = rsi_short.iloc[-2]
    prev_long = rsi_long.iloc[-2]

    if prev_short <= prev_long and curr_short > curr_long:
        return {"signal": "buy"}
    elif prev_short >= prev_long and curr_short < curr_long:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}


def bollinger_band_strategy(candles, window=3, stddev=0.1):
    if len(candles) < window:
        return {"signal": "hold"}

    closes = pd.Series([c["close"] for c in candles])

    sma = closes.rolling(window=window).mean()
    std = closes.rolling(window=window).std()

    upper = sma + stddev * std
    lower = sma - stddev * std

    price = closes.iloc[-1]
    upper_band = upper.iloc[-1]
    lower_band = lower.iloc[-1]

    if price < lower_band:
        return {"signal": "sell"}  # Price below lower band — momentum sell
    elif price > upper_band:
        return {"signal": "buy"}  # Price above upper band — momentum buy
    else:
        return {"signal": "hold"}

def momentum_volume_strategy(candles, momentum_window=51, volume_window=93):
    if len(candles) < max(momentum_window, volume_window) + 1:
        return {"signal": "hold"}

    df = pd.DataFrame(candles)
    closes = df["close"]
    volumes = df["volume"]

    momentum = closes.diff(periods=momentum_window).iloc[-1]
    avg_volume = volumes.rolling(window=volume_window).mean().iloc[-1]
    current_volume = volumes.iloc[-1]

    if avg_volume == 0 or pd.isna(avg_volume):
        return {"signal": "hold"}

    volume_conf = current_volume / avg_volume

    if momentum > 0 and volume_conf > 1.0:
        return {"signal": "sell"}
    elif momentum < 0 and volume_conf > 1.0:
        return {"signal": "buy"}
    else:
        return {"signal": "hold"}
