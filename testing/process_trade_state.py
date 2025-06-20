from datetime import timedelta
import pandas as pd
from typing import TYPE_CHECKING
from trading_2.testing.test_service import Trade
if TYPE_CHECKING:
    from trading_2.testing.condition_signals import ConditionSignal


class ProcessTrade:
    def close_lose_position(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if direction == "buy":
            if row["low_4h"] <= trade.stop_price:
                trade.exit_type = "stop"
                return True
            else:
                return False
        else:
            if row["high_4h"] >= trade.stop_price:
                trade.exit_type = "stop"
                return True
            else:
                return False

    def close_profit_position(self, row: pd.Series, direction: str, trade: Trade,
                              close_profit_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if direction == "buy":
            if row["high_4h"] >= trade.profit_price:
                trade.exit_type = "profit"
                return True
            else:
                return False
        else:
            if row["low_4h"] <= trade.profit_price:
                trade.exit_type = "profit"
                return True
            else:
                return False

    def close_by_change_direction(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        if direction == "buy":
            if row["close_1d"] < row["sma_1d"]:
                trade.exit_type = "change_direction"
                return True
            else:
                return False
        else:
            if row["close_1d"] > row["sma_1d"]:
                trade.exit_type = "change_direction"
                return True
            else:
                return False


class BaseProcessTrade(ProcessTrade):
    def process_trade_state(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None,
                            close_profit_position: "ConditionSignal"=None,
                            time_close_check=False,
                            *args, **kwargs) -> bool:
        stop_filled = self.close_lose_position(row, direction, trade, close_lose_position, *args, **kwargs)
        if stop_filled:
            return not stop_filled

        profit_filled = self.close_profit_position(row, direction, trade, close_profit_position, *args, **kwargs)
        if profit_filled:
            return not profit_filled

        change_direction_close = self.close_by_change_direction(row, direction, trade,*args, **kwargs)
        if change_direction_close:
            return not change_direction_close

        if time_close_check:
            time_close = self.time_close(row, trade,*args, **kwargs)
            if time_close:
                return not time_close

        return True

    def close_lose_position(self, row: pd.Series, direction: str, trade: Trade,
                            close_lose_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if close_lose_position:
            return close_lose_position.check_exit_condition(row, direction, trade)
        else:
            return super().close_lose_position(row, direction, trade, *args, **kwargs)

    def close_profit_position(self, row: pd.Series, direction: str, trade: Trade,
                              close_profit_position: "ConditionSignal"=None, *args, **kwargs) -> bool:
        if close_profit_position:
            return close_profit_position.check_exit_condition(row, direction, trade, *args, **kwargs)
        else:
            return super().close_profit_position(row, direction, trade, *args, **kwargs)

    def close_by_change_direction(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs):
        change_direction_close = super().close_by_change_direction(row, direction, trade, *args, **kwargs)
        trade.change_direction_price = row["close_1d"]

        return change_direction_close

    def time_close(self, row: pd.Series, trade: Trade, *args, **kwargs):
        if (pd.Timestamp(row.name) - pd.Timestamp(trade.enter_date)) >= timedelta(hours=trade.time_close_check):
            trade.close_by_time_price = row["close_4h"]
            trade.exit_type = "close_by_time"
            return True
        else:
            return False
