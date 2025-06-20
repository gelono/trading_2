from datetime import timedelta
import pandas as pd
from trading_2.testing.trade_settings import TradeSetting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from trading_2.testing.close_position_order_rule import ClosePositionOrderRule


class Trade(TradeSetting):
    def __init__(self, row: pd.Series, direction: str, stop_position_rule: "ClosePositionOrderRule",
                 profit_position_rule: "ClosePositionOrderRule", df, history):
        self.row = row
        self.df = df
        self.direction = direction
        self.id = 1
        self.day_id = row["day_id"]
        self.impulse_id = row["impulse_id"]
        self.enter_date = row.name
        self.open_price = row["close_4h"]
        self.end_delay_period = pd.Timestamp(row.name) + timedelta(hours=self.delay_period)
        self.history = history
        self.stop_price = self.get_stop_price(stop_position_rule)
        self.profit_price = self.get_profit_price(profit_position_rule)
        self.change_direction_price = 0
        self.close_by_market_price = 0
        self.close_by_time_price = 0
        self.exit_type = None
        self.weekday_1d = row["weekday_1d"]

    def get_stop_price(self, stop_position_rule: "ClosePositionOrderRule"):
        if not stop_position_rule:
            return self.open_price * (1 - (self.stop_size / 100)) if self.direction == "buy" \
                else self.open_price * (1 + (self.stop_size / 100))
        else:
            return stop_position_rule.get_stop_price(self.row, self.open_price, self.direction, self.history)

    def get_profit_price(self, profit_position_rule: "ClosePositionOrderRule"):
        if not profit_position_rule:
            return self.open_price * (1 + (self.profit_size / 100)) if self.direction == "buy" \
            else self.open_price * (1 - (self.profit_size / 100))
        else:
            return profit_position_rule.get_profit_price(self.open_price, self.direction, self.history)
