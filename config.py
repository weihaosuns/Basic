# config.py
import numpy as np

API_KEY = "57ac89e3146fa40890143447020a5a107e1e2fa2f1938ec6e59b5caeb3405bf6"
API_SECRET = "4ee21d6c66fd5113d9a54646c4cbc75e746f0913544f9b6ea7019e1f60331e2f"
BASE_URL = "https://testnet.binancefuture.com"
SYMBOL = "btcusdt"
INTERVAL = "1m"
DATA_POINTS = 150
ALLOCATION_PCT = 0.5         # 50% of wallet balance
STOP_LOSS_PCT = 0.01         # 1% SL
# TAKE_PROFIT_PCT = 0.02      # 2% TP
MAX_POSITION_USD = 7500      # 50% of 15,000
MAX_CONSECUTIVE_LOSSES = 10  # 10 SL = 10%
MAX_DRAWDOWN_PCT = 10        # 10% per day