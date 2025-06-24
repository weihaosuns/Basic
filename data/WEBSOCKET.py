# WEBSOCKET.py
import json
import logging
import time
import threading
from datetime import datetime, timezone, timedelta

from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

config_logging(logging, logging.DEBUG)

class BinanceWebSocket:
    def __init__(
            self,
            symbol: str,
            interval: str,
            contract_type: str = "perpetual",
            max_retries: int = 5,
            retry_delay: int = 5,
            max_backoff: int = 60,
            health_timeout: int = 30
    ):
        self.symbol = symbol
        self.interval = interval
        self.contract_type = contract_type
        self.client = None
        self.running = False
        self.retry_attempts = 0
        self.retry_delay = retry_delay
        self.max_backoff = max_backoff
        self.max_retries = max_retries
        self.health_timeout = health_timeout
        self.new_candle = None
        self.lock = threading.Lock()
        self.last_msg_time = datetime.now(timezone.utc)
        self.health_thread = None
        self.force_exit = False

    def message_handler(self, _, message: str):
        try:
            self.last_msg_time = datetime.now(timezone.utc)
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
            self.restart()

    def on_new_candle(self, candle):
        # Override or assign from outside
        pass

    def _start_client(self):
        self.client = UMFuturesWebsocketClient(on_message=self.message_handler)
        self.client.continuous_kline(
            pair=self.symbol,
            id=1,
            contractType=self.contract_type,
            interval=self.interval,
        )

    def _start_health_check(self):
        def monitor():
            logging.info("Health check thread started.")
            while self.running:
                time.sleep(self.health_timeout)
                time_since_last_msg = datetime.now(timezone.utc) - self.last_msg_time
                if time_since_last_msg > timedelta(seconds=self.health_timeout):
                    logging.warning(f"No message received for {self.health_timeout}s, restarting WebSocket.")
                    self.restart()
                    break  # exit health check loop after restart

        self.health_thread = threading.Thread(target=monitor, daemon=True)
        self.health_thread.start()

    def start(self):
        self.running = True
        self.retry_attempts = 0
        while self.running:
            try:
                with self.lock:
                    logging.info("Starting WebSocket connection...")
                    self._start_client()
                    self.last_msg_time = datetime.now(timezone.utc)
                    self._start_health_check()
                break  # Successful start
            except Exception as e:
                delay = min(self.retry_delay * (2 ** self.retry_attempts), self.max_backoff)
                logging.error(f"WebSocket connection failed: {e}, retrying in {delay}s")
                time.sleep(delay)
                self.retry_attempts += 1
                if self.retry_attempts >= self.max_retries:
                    logging.critical("Max retries reached.")
                    self.running = False
                    break

    def restart(self):
        if self.force_exit:
            logging.warning("Force exit set. WebSocket will not restart.")
            return
        logging.warning("Restarting WebSocket connection...")
        self.stop()
        time.sleep(self.retry_delay)
        self.start()

    def stop(self, force=False):
        with self.lock:
            self.running = False
            self.force_exit = force
            if self.client:
                try:
                    self.client.stop()
                    logging.info("WebSocket stopped.")
                except Exception as e:
                    logging.error(f"Error stopping WebSocket: {e}")
                self.client = None

# if __name__ == "__main__":
#     from config import SYMBOL, INTERVAL
#
#     class MyWebSocket(BinanceWebSocket):
#         def on_new_candle(self, candle):
#             print("New closed candle:", candle)
#
#     ws = MyWebSocket(SYMBOL, INTERVAL)
#     try:
#         ws.start()
#     except KeyboardInterrupt:
#         ws.stop()
