# WEBSOCKET.py
import json
import logging
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from config import SYMBOL, INTERVAL

config_logging(logging, logging.DEBUG)

class BinanceWebSocket:
    def __init__(self, symbol: str, interval: str, contract_type: str = "perpetual"):
        self.symbol = symbol
        self.interval = interval
        self.contract_type = contract_type
        self.client = UMFuturesWebsocketClient(on_message=self.message_handler)
        self.new_candle = None

    def message_handler(self, _, message: str):
        try:
            msg = json.loads(message)
            if msg.get("e") == "continuous_kline":
                k = msg["k"]
                if k["x"]:  # closed candle
                    self.new_candle = {
                        "timestamp": int(k["t"]),
                        "open": float(k["o"]),
                        "high": float(k["h"]),
                        "low": float(k["l"]),
                        "close": float(k["c"]),
                        "volume": float(k["v"]),
                    }
                    logging.info(f"{self.new_candle}")
                    self.on_new_candle(self.new_candle)
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def on_new_candle(self, candle):
        # Override or assign from outside
        pass

    def start(self):
        self.client.continuous_kline(
            pair=self.symbol,
            id=1,
            contractType=self.contract_type,
            interval=self.interval,
        )

    def stop(self):
        self.client.stop()

# if __name__ == "__main__":
#     ws = BinanceWebSocket(SYMBOL, INTERVAL)
#     ws.start()
