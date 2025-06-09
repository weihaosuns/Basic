import time
import logging
from config import SYMBOL, INTERVAL, weights, API_KEY, API_SECRET, BASE_URL
from data.REST import RestDataFetcher
from data.WEBSOCKET import BinanceWebSocket
from analytics.MOMENTUM import (
    sma_crossover_strategy,
    ema_momentum_strategy,
    roc_momentum_strategy,
    macd_strategy,
    rsi_strategy,
    bollinger_bands_strategy,
    momentum_with_volume_strategy,
    markov_price_strategy,
)
from analytics.AGGREGATOR import aggregate_signals
from position_manager import PositionManager
from binance.um_futures import UMFutures

logging.basicConfig(level=logging.INFO)

def main():
    # Fetch initial historical data
    rest_fetcher = RestDataFetcher()
    candles = rest_fetcher.fetch_initial_data()

    # Initialize client and position manager
    client = UMFutures(key=API_KEY, secret=API_SECRET, base_url=BASE_URL)
    position_manager = PositionManager(client, SYMBOL)

    # Update Data & Run the rest.
    class LiveWebSocket(BinanceWebSocket):
        def on_new_candle(self, candle):
            candles.append(candle)
            logging.info(f"Appended new candle. Total candles: {len(candles)}")

            # trigger analytics
            strategies = [
                sma_crossover_strategy,
                roc_momentum_strategy,
                ema_momentum_strategy,
                macd_strategy,
                rsi_strategy,
                bollinger_bands_strategy,
                momentum_with_volume_strategy,
                markov_price_strategy,
            ]
            agg_signal = aggregate_signals(candles, strategies, weights)
            logging.info(f"New Candle Signal: {agg_signal}")

            price = candle["close"]
            position_manager.manage_position(agg_signal["signal"], price)

    # Start WebSocket
    ws = LiveWebSocket(symbol=SYMBOL, interval=INTERVAL)
    ws.candles = candles
    ws.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws.stop()
        position_manager.shutdown()
        logging.info("Stopped WebSocket and closed all positions.")

if __name__ == "__main__":
    main()