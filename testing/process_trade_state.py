import pandas as pd
from typing import TYPE_CHECKING

from trading_2.testing.trade_services import Trade

if TYPE_CHECKING:
    from trading_2.testing.condition_signal import ConditionSignal


class ProcessTrade:
    def close_lose_position(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if direction == "buy":
            return row["low_4h"] <= trade.stop_price
        else:
            return row["high_4h"] >= trade.stop_price

    def close_profit_position(self, row: pd.Series, direction: str, trade: Trade,
                              close_profit_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if direction == "buy":
            return row["high_4h"] >= trade.profit_price
        else:
            return row["low_4h"] <= trade.profit_price

    def close_by_change_direction(self, row: pd.Series, direction: str, *args, **kwargs):
        if direction == "buy":
            return row["close_1d"] < row["sma_1d"]
        else:
            return row["close_1d"] > row["sma_1d"]


class BaseProcessTrade(ProcessTrade):
    def process_trade_state(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None,
                            close_profit_position: "ConditionSignal"=None,
                            *args, **kwargs) -> (bool, str):
        stop_filled = self.close_lose_position(row, direction, trade, close_lose_position, *args, **kwargs)
        if stop_filled:
            return not stop_filled, "stop"

        profit_filled = self.close_profit_position(row, direction, trade, close_profit_position, *args, **kwargs)
        if profit_filled:
            return not profit_filled, "profit"

        change_direction_close = self.close_by_change_direction(row, direction, *args, **kwargs)
        if change_direction_close:
            trade.change_direction_price = row["close_1d"]
            return not change_direction_close, "change_direction"

        return True, ""

    def close_lose_position(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if close_lose_position:
            return close_lose_position.check_exit_condition(row, direction, trade)
        else:
            return super().close_lose_position(row, direction, trade, *args, **kwargs)

    def close_profit_position(self, row: pd.Series, direction: str, trade: Trade,
                              close_profit_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if close_profit_position:
            return close_profit_position.check_exit_condition(row, direction, trade)
        else:
            return super().close_profit_position(row, direction, trade, *args, **kwargs)

    def close_by_change_direction(self, row: pd.Series, direction: str, *args, **kwargs):
        return super().close_by_change_direction(row, direction, *args, **kwargs)
