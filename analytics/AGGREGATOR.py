def aggregate_signals(candles, strategies, weights=None):
    """
    Aggregate multiple strategies into a single signal using majority-weighted voting.

    Parameters:
    - candles: deque or list of candle dicts
    - strategies: list of strategy functions that take candles and return dict {signal: str}
    - weights: list of floats for weighting strategies; if None, equal weights

    Returns:
    - dict with 'signal' only
    """
    # Leave for future if weights are required.
    # if weights is None:
    #     weights = [1.0] * len(strategies)
    #
    # assert len(weights) == len(strategies), "Weights and strategies length mismatch"

    threshold = 0.7  # e.g., 5 out of 7 signals required.

    buy_votes = sum(1 for strat in strategies if strat(candles).get("signal", "hold") == "buy")
    sell_votes = sum(1 for strat in strategies if strat(candles).get("signal", "hold") == "sell")
    total = len(strategies)

    if buy_votes / total >= threshold:
        return {"signal": "buy"}
    elif sell_votes / total >= threshold:
        return {"signal": "sell"}
    else:
        return {"signal": "hold"}
