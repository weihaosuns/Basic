# data/REST.py

import logging
from collections import deque
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from config import SYMBOL, INTERVAL, DATA_POINTS

# config_logging(logging, logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

class RestDataFetcher:
    def __init__(self):
        self.client = UMFutures()

    def fetch_initial_data(self):
        raw_klines = self.client.continuous_klines(
            pair=SYMBOL.upper(),
            contractType="PERPETUAL",
            interval=INTERVAL,
            limit=DATA_POINTS
        )
        logging.info(f"Fetched {len(raw_klines)} klines")

        candles = deque(maxlen=DATA_POINTS)
        for k in raw_klines:
            candle = {
                "timestamp": int(k[0]),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            candles.append(candle)
        return candles

# if __name__ == "__main__":
#     fetcher = RestDataFetcher()
#     candles = fetcher.fetch_initial_data()
#     for c in candles:
#         print(c)