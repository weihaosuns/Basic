# config.py
import numpy as np

API_KEY = "57ac89e3146fa40890143447020a5a107e1e2fa2f1938ec6e59b5caeb3405bf6"
API_SECRET = "4ee21d6c66fd5113d9a54646c4cbc75e746f0913544f9b6ea7019e1f60331e2f"
BASE_URL = "https://testnet.binancefuture.com"
SYMBOL = "btcusdt"
INTERVAL = "1m"
DATA_POINTS = 300
ALLOCATION_PCT = 0.05       # 5% of wallet balance
STOP_LOSS_PCT = 0.01        # 1% SL
TAKE_PROFIT_PCT = 0.02      # 2% TP
MAX_POSITION_USD = 750      # 5% of 15,000
MAX_CONSECUTIVE_LOSSES = 5  # 5 SL = 5%
MAX_DRAWDOWN_PCT = 0.05     # 5% per day

extracted_weights = [{'buy': np.float64(0.03244280654346815),
  'sell': np.float64(0.03804849089987302)},
 {'buy': np.float64(-0.05297275052732096),
  'sell': np.float64(0.03397235873034015)},
 {'buy': np.float64(0.001761384766475957),
  'sell': np.float64(0.005894839787707059)},
 {'buy': np.float64(-0.004270414821777813),
  'sell': np.float64(-0.0068446179029911895)},
 {'buy': np.float64(-0.001857576623100386),
  'sell': np.float64(-0.07633625060985212)},
 {'buy': np.float64(-8.465059911680986e-05),
  'sell': np.float64(0.00034531225160149215)},
 {'buy': np.float64(0.020615215447378748),
  'sell': np.float64(0.10036010981203138)},
 {'buy': np.float64(0.0075037459512008724),
  'sell': np.float64(-0.12022576934241866)}]

weights = [abs(w['buy']) + abs(w['sell']) for w in extracted_weights]