import logging
from binance.um_futures import UMFutures
from config import (
    ALLOCATION_PCT,
    STOP_LOSS_PCT,
    # TAKE_PROFIT_PCT,
    MAX_POSITION_USD,
    MAX_CONSECUTIVE_LOSSES,
    MAX_DRAWDOWN_PCT,
)
from risk_manager import RiskManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

class PositionManager:
    def __init__(self, client: UMFutures, symbol: str):
        self.client = client
        self.symbol = symbol.upper()
        self.position = 0.0
        self.entry_price = 0.0
        self.leverage = 1

        starting_balance = self.get_wallet_balance()
        self.risk_manager = RiskManager(
            max_position_usd=MAX_POSITION_USD,
            max_consecutive_losses=MAX_CONSECUTIVE_LOSSES,
            max_drawdown_pct=MAX_DRAWDOWN_PCT,
            starting_balance_usd=starting_balance
        )

    def get_wallet_balance(self):
        try:
            account_info = self.client.account()
            return float(account_info['totalWalletBalance'])
        except Exception as e:
            logging.error(f"Error fetching wallet balance: {e}")
            return 0.0

    def update_position_info(self):
        try:
            positions = self.client.get_position_risk()
            pos = next((p for p in positions if p["symbol"] == self.symbol), None)
            if pos:
                self.position = float(pos["positionAmt"])
                self.entry_price = float(pos["entryPrice"])
                self.leverage = int(pos.get("leverage", self.leverage))
            else:
                self.position = 0.0
                self.entry_price = 0.0
        except Exception as e:
            logging.error(f"Error updating position info: {e}")

    def cancel_open_conditional_orders(self):
        try:
            response = self.client.cancel_open_orders(symbol=self.symbol)
            logging.info(f"Canceled all open orders: {response}")
        except Exception as e:
            logging.error(f"Failed to cancel open orders: {e}")

    def close_position(self):
        self.update_position_info()
        side = "SELL" if self.position > 0 else "BUY"
        qty = abs(self.position)
        if qty == 0:
            return

        try:
            self.cancel_open_conditional_orders()
            self.client.new_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=round(qty, 3)
            )
            logging.info(f"Closed position: {side} {qty:.4f} {self.symbol}")

            self.risk_manager.track_risk_after_trade(self.get_wallet_balance())

        except Exception as e:
            logging.error(f"Failed to close position: {e}")

    def open_position(self, side: str, quantity: float, price: float):
        opposite = "SELL" if side == "BUY" else "BUY"
        try:
            self.cancel_open_conditional_orders()

            self.client.new_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=round(quantity, 3)
            )
            logging.info(f"Opened {side} position with {quantity:.4f} {self.symbol}")

            # SL/TP prices
            sl_price = price * (1 - STOP_LOSS_PCT) if side == "BUY" else price * (1 + STOP_LOSS_PCT)
            # tp_price = price * (1 + TAKE_PROFIT_PCT) if side == "BUY" else price * (1 - TAKE_PROFIT_PCT)

            self.client.new_order(
                symbol=self.symbol,
                side=opposite,
                type="STOP_MARKET",
                stopPrice=round(sl_price, 2),
                closePosition=True,
                timeInForce="GTC"
            )
            # self.client.new_order(
            #     symbol=self.symbol,
            #     side=opposite,
            #     type="TAKE_PROFIT_MARKET",
            #     stopPrice=round(tp_price, 2),
            #     closePosition=True,
            #     timeInForce="GTC"
            # )

            logging.info(f"SL at {sl_price:.2f}")
            # , TP at {tp_price:.2f}")

        except Exception as e:
            logging.error(f"Failed to open position: {e}")

    def manage_position(self, signal: str, price: float):
        self.update_position_info()

        if signal == "hold":
            logging.info("Signal is hold. No action taken.")
            return

        wallet = self.get_wallet_balance()
        if price == 0:
            logging.error("Price is zero, cannot calculate quantity.")
            return

        usdt_alloc = min(wallet * ALLOCATION_PCT, MAX_POSITION_USD)
        qty = usdt_alloc / price

        # Check risk limits before proceeding
        if not self.risk_manager.can_open_position(self.symbol, wallet, usdt_alloc):
            logging.warning("Risk limits prevent trade. Skipping.")
            return

        logging.info(f"Signal: {signal.upper()}, Allocation: ${usdt_alloc:.2f}, Quantity: {qty:.4f} {self.symbol}")

        current_side = "buy" if self.position > 0 else ("sell" if self.position < 0 else None)
        if signal.lower() == current_side:
            logging.info("Already in the same direction. No action taken.")
            return

        if self.position != 0:
            logging.info("Reversing position by closing existing position...")
            self.close_position()

        self.open_position(signal.upper(), qty, price)

        if self.risk_manager.is_drawdown_exceeded or self.risk_manager.has_max_losses():
            logging.warning("Post-trade: risk limits breached. Exiting.")
            self.shutdown()
            raise RuntimeError("Risk limits breached. Program terminated.")

    def shutdown(self):
        logging.info("Shutting down: closing all positions and cancelling orders...")
        self.cancel_open_conditional_orders()
        self.close_position()
        raise SystemExit("Risk limits breached. Shutting down.")