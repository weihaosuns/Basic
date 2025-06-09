import logging
import time


class RiskManager:
    def __init__(self, max_position_usd, max_consecutive_losses, max_drawdown_pct, starting_balance_usd):
        self.max_position_usd = max_position_usd
        self.max_consecutive_losses = max_consecutive_losses
        self.max_drawdown_pct = max_drawdown_pct
        self.starting_balance_usd = starting_balance_usd

        self.current_drawdown_pct = 0
        self.peak_balance = starting_balance_usd
        self.consecutive_losses = {}
        self.open_positions = {}

    def can_open_position(self, symbol, current_balance):
        # Check drawdown
        self.peak_balance = max(self.peak_balance, current_balance)
        self.current_drawdown_pct = 100.0 * (self.peak_balance - current_balance) / self.peak_balance

        if self.current_drawdown_pct > self.max_drawdown_pct:
            logging.warning(f"Drawdown {self.current_drawdown_pct:.2f}% exceeds max allowed {self.max_drawdown_pct}%")
            return False

        # Check max position
        if symbol in self.open_positions:
            position_usd = self.open_positions[symbol]["usd_value"]
            if position_usd >= self.max_position_usd:
                logging.warning(f"Symbol {symbol} position ${position_usd:.2f} exceeds max ${self.max_position_usd}")
                return False

        # Check consecutive losses
        if self.consecutive_losses.get(symbol, 0) >= self.max_consecutive_losses:
            logging.warning(f"{symbol} reached max consecutive losses ({self.max_consecutive_losses})")
            return False

        return True

    def record_position(self, symbol, usd_value):
        self.open_positions[symbol] = {
            "usd_value": usd_value,
            "entry_time": time.time()
        }

    def close_position(self, symbol, pnl_usd):
        # Update drawdown tracking
        if pnl_usd < 0:
            self.consecutive_losses[symbol] = self.consecutive_losses.get(symbol, 0) + 1
        else:
            self.consecutive_losses[symbol] = 0

        if symbol in self.open_positions:
            del self.open_positions[symbol]
