import numpy as np
import pandas as pd
from trading_2.testing.interfaces.close_position_rules import ClosePositionOrderRule


class StopProfitOrderATR(ClosePositionOrderRule):
    def get_stop_price(self, row: pd.Series, open_price: float, direction: str, history: dict = None):
        atr = self._get_atr(history)
        stop_size = atr * self.atr_coefficient_stop
        stop_price = open_price * (1 - (stop_size / 100)) if direction == "buy" \
            else open_price * (1 + (stop_size / 100))

        return stop_price

    def get_profit_price(self, open_price: float, direction: str, history: dict = None):
        atr = self._get_atr(history)
        profit_size = atr * self.atr_coefficient_profit
        profit_price = open_price * (1 + (profit_size / 100)) if direction == "buy" \
            else open_price * (1 - (profit_size / 100))

        return profit_price

    def _get_atr(self, history: dict = None):
        if history is None:
            raise ValueError("Missing history data")

        avg_range = []
        for row in list(history.values())[:self.atr_period]:
            avg_range.append(100 * (row["high_4h"] - row["low_4h"]) / row["low_4h"])

        return float(np.mean(avg_range))


class StopOrderBehindExtremum(ClosePositionOrderRule):
    def get_stop_price(self, row: pd.Series, open_price: float, direction: str, history: dict = None):
        if direction == "buy":
            low_list = [row["low_4h"] for row in list(history.values())[:self.stop_lookback_period-1]]
            low_list.append(row["low_4h"])
            stop_price = min(low_list) * 0.999
        else:
            low_list = [row["high_4h"] for row in list(history.values())[:self.stop_lookback_period-1]]
            low_list.append(row["high_4h"])
            stop_price = max(low_list) * 1.001

        return stop_price

    def get_profit_price(self, open_price: float, direction: str, history: dict = None):
        pass