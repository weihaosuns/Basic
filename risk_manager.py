import logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

class RiskManager:
    """
    Manages risk limits: max position size, max consecutive losses, and max drawdown.
    Tracks loss streak and drawdown status.
    """

    def __init__(self, max_position_usd, max_consecutive_losses, max_drawdown_pct, starting_balance_usd):
        self.max_position_usd = max_position_usd
        self.max_consecutive_losses = max_consecutive_losses
        self.max_drawdown_pct = max_drawdown_pct
        self.starting_balance_usd = starting_balance_usd

        self.loss_streak = 0
        self.max_drawdown_triggered = False

        self.peak_balance = starting_balance_usd
        self.current_drawdown_pct = 0.0

        self.open_positions = {}


    def update_balance(self, current_balance):
        """Update peak balance and current drawdown percentage."""
        logging.debug(f"[Risk] Updating balance: current={current_balance:.2f}, peak={self.peak_balance:.2f}")

        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
            logging.info(f"[Risk] New peak balance set: {current_balance:.2f}")

        if self.peak_balance > 0:
            self.current_drawdown_pct = 100 * (self.peak_balance - current_balance) / self.peak_balance
        else:
            self.current_drawdown_pct = 0

    def can_open_position(self, symbol, current_balance, position_usd):
        """
        Check if a new position can be opened considering drawdown,
        max position size, and consecutive losses.
        """
        self.update_balance(current_balance)

        if self.current_drawdown_pct > self.max_drawdown_pct:
            logging.warning(f"Drawdown {self.current_drawdown_pct:.2f}% exceeds max allowed {self.max_drawdown_pct}%")
            self.max_drawdown_triggered = True
            return False

        if position_usd > self.max_position_usd:
            logging.warning(f"Position size ${position_usd:.2f} exceeds max allowed ${self.max_position_usd}")
            return False

        if self.loss_streak >= self.max_consecutive_losses:
            logging.warning(f"Max consecutive losses reached: {self.loss_streak} >= {self.max_consecutive_losses}")
            return False

        return True

    def track_risk_after_trade(self, wallet_balance):
        """
        Update loss streak and drawdown status after a trade.
        Call this after closing or settling a position.
        """
        # logging.debug(f"[Risk] Wallet balance: {wallet_balance:.2f}")
        # logging.debug(f"[Risk] Starting balance: {self.starting_balance_usd:.2f}")
        # logging.debug(f"[Risk] Peak balance before update: {self.peak_balance:.2f}")
        pnl_pct = 100 * (wallet_balance - self.starting_balance_usd) / self.starting_balance_usd
        if pnl_pct < 0:
            self.loss_streak += 1
            logging.warning(f"Loss streak incremented: {self.loss_streak}")
        else:
            if self.loss_streak > 0:
                logging.info(f"Loss streak reset from {self.loss_streak} to 0")
            self.loss_streak = 0



        self.update_balance(wallet_balance)

        # logging.debug(f"[Risk] PnL % from start: {pnl_pct}%")
        # logging.debug(f"[Risk] Peak balance after update: {self.peak_balance:.2f}")
        # logging.debug(f"[Risk] Current drawdown %: {self.current_drawdown_pct}%")
        # logging.debug(f"[Risk] Max drawdown %: {self.max_drawdown_pct}%")

        if pnl_pct <= -self.max_drawdown_pct:
            logging.critical(f"Drawdown limit breached: {pnl_pct}%")
            self.max_drawdown_triggered = True

    def reset(self):
        """Reset risk state to initial."""
        self.loss_streak = 0
        self.max_drawdown_triggered = False
        self.current_drawdown_pct = 0.0
        self.peak_balance = self.starting_balance_usd
        self.open_positions.clear()

    @property
    def is_drawdown_exceeded(self):
        return self.max_drawdown_triggered

    def has_max_losses(self):
        return self.loss_streak >= self.max_consecutive_losses
