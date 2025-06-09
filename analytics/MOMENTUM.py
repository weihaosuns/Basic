def sma_crossover_strategy(candles, short_window=10, long_window=50):
    closes = [c["close"] for c in list(candles)]
    short_sma = sum(closes[-short_window:]) / short_window
    long_sma = sum(closes[-long_window:]) / long_window

    prev_short_sma = sum(closes[-short_window-1:-1]) / short_window
    prev_long_sma = sum(closes[-long_window-1:-1]) / long_window

    if prev_short_sma <= prev_long_sma and short_sma > long_sma:
        return {"signal": "buy", "confidence": 0.9}
    elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
        return {"signal": "sell", "confidence": 0.9}
    else:
        return {"signal": "hold", "confidence": 0.0}

def roc_momentum_strategy(candles, period=14):
    closes = [c["close"] for c in list(candles)]
    roc_current = (closes[-1] - closes[-period-1]) / closes[-period-1]
    roc_prev = (closes[-2] - closes[-period-2]) / closes[-period-2]

    if roc_current > 0 and roc_current > roc_prev:
        return {"signal": "buy", "confidence": abs(roc_current)}
    elif roc_current < 0 and roc_current < roc_prev:
        return {"signal": "sell", "confidence": abs(roc_current)}
    else:
        return {"signal": "hold", "confidence": 0.0}

def ema(prices, period):
    k = 2 / (period + 1)
    ema_values = []
    ema_values.append(prices[0])  # first EMA is first price
    for price in prices[1:]:
        ema_prev = ema_values[-1]
        ema_new = price * k + ema_prev * (1 - k)
        ema_values.append(ema_new)
    return ema_values

def ema_momentum_strategy(candles, short_period=12, long_period=26):
    closes = [c["close"] for c in list(candles)]
    short_ema = ema(closes, short_period)[-1]
    long_ema = ema(closes, long_period)[-1]

    if short_ema > long_ema:
        return {"signal": "buy", "confidence": 0.9}
    elif short_ema < long_ema:
        return {"signal": "sell", "confidence": 0.9}
    else:
        return {"signal": "hold", "confidence": 0.0}

def macd_strategy(candles, fast_period=12, slow_period=26, signal_period=9):
    closes = [c["close"] for c in list(candles)]

    def ema(prices, period):
        k = 2 / (period + 1)
        ema_values = [prices[0]]
        for price in prices[1:]:
            ema_values.append(price * k + ema_values[-1] * (1 - k))
        return ema_values

    fast_ema = ema(closes, fast_period)
    slow_ema = ema(closes, slow_period)
    macd_line = [f - s for f, s in zip(fast_ema[-len(slow_ema):], slow_ema)]
    signal_line = ema(macd_line, signal_period)

    if len(macd_line) < 2 or len(signal_line) < 2:
        return {"signal": "hold", "confidence": 0.0}

    # MACD crossover
    if macd_line[-2] <= signal_line[-2] and macd_line[-1] > signal_line[-1]:
        return {"signal": "buy", "confidence": abs(macd_line[-1] - signal_line[-1])}
    elif macd_line[-2] >= signal_line[-2] and macd_line[-1] < signal_line[-1]:
        return {"signal": "sell", "confidence": abs(macd_line[-1] - signal_line[-1])}
    else:
        return {"signal": "hold", "confidence": 0.0}

def rsi_strategy(candles, period=14, overbought=70, oversold=30):
    closes = [c["close"] for c in list(candles)]

    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    if len(gains) < period:
        return {"signal": "hold", "confidence": 0.0}

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    if rsi > overbought:
        # Sell signal when overbought
        confidence = (rsi - overbought) / (100 - overbought)
        return {"signal": "sell", "confidence": confidence}
    elif rsi < oversold:
        # Buy signal when oversold
        confidence = (oversold - rsi) / oversold
        return {"signal": "buy", "confidence": confidence}
    else:
        return {"signal": "hold", "confidence": 0.0}

import math

def bollinger_bands_strategy(candles, window=20, num_std=2):
    closes = [c["close"] for c in list(candles)]
    if len(closes) < window:
        return {"signal": "hold", "confidence": 0.0}

    sma = sum(closes[-window:]) / window
    variance = sum((x - sma) ** 2 for x in closes[-window:]) / window
    std_dev = math.sqrt(variance)

    upper_band = sma + num_std * std_dev
    lower_band = sma - num_std * std_dev
    last_close = closes[-1]

    # If price breaks above upper band -> strong momentum up (buy)
    if last_close > upper_band:
        confidence = (last_close - upper_band) / upper_band
        return {"signal": "buy", "confidence": min(confidence, 1.0)}

    # If price breaks below lower band -> strong momentum down (sell)
    elif last_close < lower_band:
        confidence = (lower_band - last_close) / lower_band
        return {"signal": "sell", "confidence": min(confidence, 1.0)}

    else:
        return {"signal": "hold", "confidence": 0.0}

def momentum_with_volume_strategy(candles, momentum_period=20, volume_period=20):
    closes = [c["close"] for c in list(candles)]
    volumes = [c["volume"] for c in list(candles)]

    if len(closes) < momentum_period or len(volumes) < volume_period:
        return {"signal": "hold", "confidence": 0.0}

    price_change = closes[-1] - closes[-momentum_period]
    avg_volume = sum(volumes[-volume_period:]) / volume_period
    current_volume = volumes[-1]

    volume_conf = current_volume / avg_volume if avg_volume > 0 else 0

    if price_change > 0 and volume_conf > 1.0:
        return {"signal": "buy", "confidence": min(volume_conf, 2.0)/2}  # confidence capped at 1
    elif price_change < 0 and volume_conf > 1.0:
        return {"signal": "sell", "confidence": min(volume_conf, 2.0)/2}
    else:
        return {"signal": "hold", "confidence": 0.0}

from collections import Counter

def build_markov_chain_from_prices(candles):
    states = []
    for i in range(1, len(candles)):
        if candles[i]["close"] > candles[i-1]["close"]:
            states.append("buy")
        elif candles[i]["close"] < candles[i-1]["close"]:
            states.append("sell")
        else:
            states.append(states[-1] if states else "buy")  # carry last state or default to buy

    # Build transition counts
    transitions = Counter()
    for i in range(1, len(states)):
        prev_state = states[i-1]
        curr_state = states[i]
        transitions[(prev_state, curr_state)] += 1

    # Convert to transition probabilities
    matrix = {"buy": {"buy": 0.0, "sell": 0.0}, "sell": {"buy": 0.0, "sell": 0.0}}
    for from_state in ["buy", "sell"]:
        total = sum(transitions[(from_state, to)] for to in ["buy", "sell"])
        if total > 0:
            for to_state in ["buy", "sell"]:
                matrix[from_state][to_state] = transitions[(from_state, to_state)] / total

    return matrix, states[-1]  # last state is current momentum direction

def markov_price_strategy(candles):
    matrix, last_state = build_markov_chain_from_prices(candles)
    probs = matrix[last_state]
    if probs["buy"] > probs["sell"]:
        return {"signal": "buy", "confidence": probs["buy"]}
    elif probs["sell"] > probs["buy"]:
        return {"signal": "sell", "confidence": probs["sell"]}
    else:
        return {"signal": "hold", "confidence": 0.0}
