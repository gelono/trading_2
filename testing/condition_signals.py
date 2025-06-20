from datetime import timedelta
import numpy as np
import pandas as pd
from trading_2.testing.interfaces.enter_exit_signals import ConditionSignal
from trading_2.testing.process_trade_state import Trade


class ProfitByMomentum(ConditionSignal):
    @staticmethod
    def get_history_close(row: pd.Series, trade: Trade):
        history_close = [
            trade.df.loc[pd.Timestamp(row.name) - timedelta(hours=delta)]["close_4h"]
            for delta in range(0, (trade.momentum_period * 4) + 4, 4)
        ]

        return history_close

    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        pass

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        history_close = self.get_history_close(row, trade)
        if direction == "buy":
            if history_close[0] < history_close[trade.momentum_period]:
                trade.close_by_market_price = history_close[0]
                trade.exit_type = "close_by_market"
                return True
            else:
                return False
        else:
            if history_close[0] > history_close[trade.momentum_period]:
                trade.close_by_market_price = history_close[0]
                trade.exit_type = "close_by_market"
                return True
            else:
                return False


class WorkPeriodCrossMAEarly(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                current_row["close_4h"] < current_row["sma_4h"] and
                prev_4h["close_4h"] >= prev_4h["sma_4h"] and
                current_row["low_4h"] >= (current_row["sma_4h"] * (1 - self.extremum_to_ma_filter))
            )
        else:
            return (
                current_row["close_4h"] > current_row["sma_4h"] and
                prev_4h["close_4h"] <= prev_4h["sma_4h"] and
                current_row["high_4h"] <= (current_row["sma_4h"] * (1 + self.extremum_to_ma_filter))
            )

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodCrossMALate(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                current_row["close_4h"] > current_row["sma_4h"] and
                prev_4h["close_4h"] <= prev_4h["sma_4h"]
            )
        else:
            return (
                current_row["close_4h"] < current_row["sma_4h"] and
                prev_4h["close_4h"] >= prev_4h["sma_4h"]
            )

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodCrossMAWithDelay(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        prev_8h = history.get("prev_8h")

        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                current_row["close_4h"] < current_row["sma_4h"] and
                prev_4h["close_4h"] < prev_4h["sma_4h"] and
                prev_8h["close_4h"] >= prev_8h["sma_4h"]
            )
        else:
            return (
                current_row["close_4h"] > current_row["sma_4h"] and
                prev_4h["close_4h"] > prev_4h["sma_4h"] and
                prev_8h["close_4h"] <= prev_8h["sma_4h"]
            )

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class ImpulsPeriodDirection(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["close_1d"] > current_row["sma_1d"]
        else:
            return current_row["close_1d"] < current_row["sma_1d"]

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodKnifeFilter(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["low_4h"] >= min([row["low_4h"] for row in list(history.values())[:self.stop_lookback_period-1]])
        else:
            return current_row["high_4h"] <= max([row["high_4h"] for row in list(history.values())[:self.stop_lookback_period-1]])

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class StrategicPeriodDirection(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["close_1w"] > current_row["sma_1w"]
        else:
            return current_row["close_1w"] < current_row["sma_1w"]

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class StrategicPeriodFilter(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["close_4h"] > current_row["close_1w"]
        else:
            return current_row["close_4h"] < current_row["close_1w"]

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodCloseReverse(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        prev_8h = history.get("prev_8h")

        if direction == "buy":
            return current_row["close_4h"] > prev_4h["close_4h"] and prev_4h["close_4h"] < prev_8h["close_4h"]
        else:
            return current_row["close_4h"] < prev_4h["close_4h"] and prev_4h["close_4h"] > prev_8h["close_4h"]

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodVolumeSignalOrMACrossLate(ConditionSignal):
    def __init__(self, volume_coefficient):
        self.volume_coefficient = volume_coefficient
        self.work_period_cross_ma_late = WorkPeriodCrossMALate()

    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        avg_vol = np.mean([row["volume_4h"] for row in history.values()])

        if direction == "buy":
            return (
                current_row["low_4h"] < current_row["sma_4h"] and
                current_row["volume_4h"] >= avg_vol * self.volume_coefficient and
                current_row["low_4h"] < history.get("prev_4h")["low_4h"]
            ) or self.work_period_cross_ma_late.check_condition(current_row, history, direction)
        else:
            return (
                current_row["high_4h"] > current_row["sma_4h"] and
                current_row["volume_4h"] >= avg_vol * self.volume_coefficient and
                current_row["high_4h"] > history.get("prev_4h")["high_4h"]
            ) or self.work_period_cross_ma_late.check_condition(current_row, history, direction)

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodVolumeSignal(ConditionSignal):
    def __init__(self, volume_coefficient):
        self.volume_coefficient = volume_coefficient

    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        avg_vol = np.mean([row["volume_4h"] for row in history.values()])

        if direction == "buy":
            return (
                current_row["low_4h"] < current_row["sma_4h"] and
                current_row["volume_4h"] >= avg_vol * self.volume_coefficient and
                current_row["low_4h"] < history.get("prev_4h")["low_4h"]
            )
        else:
            return (
                current_row["high_4h"] > current_row["sma_4h"] and
                current_row["volume_4h"] >= avg_vol * self.volume_coefficient and
                current_row["high_4h"] > history.get("prev_4h")["high_4h"]
            )

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodCrossMAEarlyOrLate(ConditionSignal):
    def __init__(self):
        self.work_period_cross_ma_late = WorkPeriodCrossMALate()

    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                current_row["close_4h"] < current_row["sma_4h"] and
                prev_4h["close_4h"] >= prev_4h["sma_4h"] and
                current_row["low_4h"] >= (current_row["sma_4h"] * (1 - self.extremum_to_ma_filter))
            ) or self.work_period_cross_ma_late.check_condition(current_row, history, direction)
        else:
            return (
                current_row["close_4h"] > current_row["sma_4h"] and
                prev_4h["close_4h"] <= prev_4h["sma_4h"] and
                current_row["high_4h"] <= (current_row["sma_4h"] * (1 + self.extremum_to_ma_filter))
            ) or self.work_period_cross_ma_late.check_condition(current_row, history, direction)

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass


class WorkPeriodExtremumToMAFilter(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["low_4h"] >= (current_row["sma_4h"] * (1 - self.extremum_to_ma_filter))
        else:
            return current_row["high_4h"] <= (current_row["sma_4h"] * (1 + self.extremum_to_ma_filter))

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass
