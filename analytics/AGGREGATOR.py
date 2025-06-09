def aggregate_signals(candles, strategies, weights=None):
    """
    Aggregate multiple momentum strategies into a single signal.

    Parameters:
    - candles: deque or list of candle dicts
    - strategies: list of strategy functions that take candles and return dict {signal, confidence}
    - weights: list of floats for weighting strategies; if None, equal weights

    Returns:
    - dict with 'signal' and 'confidence'
    """

    if weights is None:
        weights = [1.0] * len(strategies)

    assert len(weights) == len(strategies), "Weights and strategies length mismatch"

    # Map signal string to numeric for aggregation
    signal_map = {"buy": 1, "sell": -1, "hold": 0}

    weighted_score = 0.0
    total_weight = 0.0
    weighted_confidences = {"buy": 0.0, "sell": 0.0, "hold": 0.0}

    for strat, w in zip(strategies, weights):
        result = strat(candles)
        sig = result["signal"].lower()
        conf = result["confidence"]

        if sig not in signal_map:
            sig = "hold"

        weighted_score += signal_map[sig] * conf * w
        weighted_confidences[sig] += conf * w
        total_weight += w

    # Decide final signal based on sign of weighted_score
    if weighted_score > 0:
        final_signal = "buy"
    elif weighted_score < 0:
        final_signal = "sell"
    else:
        final_signal = "hold"

    # Normalize confidence to max 1.0
    final_confidence = min(weighted_confidences[final_signal] / total_weight, 1.0)

    return {"signal": final_signal, "confidence": final_confidence}
