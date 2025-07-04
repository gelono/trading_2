from datetime import timedelta
from typing import Dict, Tuple

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


class WorkPeriodStochasticEnterExit(ConditionSignal):
    @staticmethod
    def get_current_stochastic_from_history(
            history: Dict[str, pd.Series],
            k_period: int = 12,
            d_period: int = 3
    ) -> tuple[float, float]:
        """
        Рассчитывает стохастический осциллятор (%K и %D) по history-словарю с Series.

        :param history: словарь вида {label: pd.Series}, где Series содержит high/low/close
        :param k_period: период для расчета %K
        :param d_period: период для расчета %D
        :return: (текущее значение %K, текущее значение %D)
        """
        if len(history) < k_period + d_period - 1:
            raise ValueError(f"Недостаточно данных в history: минимум {k_period + d_period - 1} записей")

        # Упорядочим по времени (по возрастанию часов)
        sorted_history = sorted(history.items(), key=lambda x: int(x[0].split("_")[1][:-1]))
        # recent = [item[1] for item in sorted_history][- (k_period + d_period - 1):]
        recent = [item[1] for item in sorted_history][:k_period + d_period - 1]

        highs = [r["high_4h"] for r in recent]
        lows = [r["low_4h"] for r in recent]
        closes = [r["close_4h"] for r in recent]

        # rolling %K
        percent_k_series = []
        # for i in range(len(recent) - k_period + 1):
        i = d_period - 1
        step = 0
        while i >= 0:
            window_highs = highs[i:k_period+d_period-1+step]
            window_lows = lows[i:k_period+d_period-1+step]
            window_closes = closes[i:k_period+d_period-1+step]
            current_close = window_closes[0]
            i -= 1
            step -= 1

            highest_high = max(window_highs)
            lowest_low = min(window_lows)
            if highest_high == lowest_low:
                percent_k = 0  # avoid division by zero
            else:
                percent_k = 100 * (current_close - lowest_low) / (highest_high - lowest_low)

            percent_k_series.append(percent_k)

        current_k = percent_k_series[-1]
        current_d = sum(percent_k_series[-d_period:]) / d_period

        return current_k, current_d

    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_stochastic_k, prev_stochastic_d = self.get_current_stochastic_from_history(
            history, self.stochastic_k, self.stochastic_d)

        history["prev_0h"] = current_row

        stochastic_k, stochastic_d = self.get_current_stochastic_from_history(
            history, self.stochastic_k, self.stochastic_d)

        if direction == "buy":
            return prev_stochastic_k <= prev_stochastic_d and stochastic_k > stochastic_d #and prev_stochastic_k > 50
        else:
            return prev_stochastic_k >= prev_stochastic_d and stochastic_k < stochastic_d #and prev_stochastic_k < 50

    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        deltas_dict = {f"prev_{i}h": i for i in range(4, trade.operational_history_period * 4 + 4, 4)}
        delta_map = {label: timedelta(hours=hours) for label, hours in deltas_dict.items()}
        history = {label: trade.df.loc[pd.Timestamp(row.name) - delta] for label, delta in delta_map.items()
                   if (pd.Timestamp(row.name) - delta) in trade.df.index}

        prev_stochastic_k, prev_stochastic_d = self.get_current_stochastic_from_history(
            history, self.stochastic_k, self.stochastic_d)

        history["prev_0h"] = row

        stochastic_k, stochastic_d = self.get_current_stochastic_from_history(
            history, self.stochastic_k, self.stochastic_d)

        if direction == "buy":
            if prev_stochastic_k >= prev_stochastic_d and stochastic_k < stochastic_d and prev_stochastic_k >= 70:
                trade.close_by_market_price = row["close_4h"]
                trade.exit_type = "close_by_market"
                return True
            else:
                return False
        else:
            if prev_stochastic_k <= prev_stochastic_d and stochastic_k > stochastic_d and prev_stochastic_k <= 30:
                trade.close_by_market_price = row["close_4h"]
                trade.exit_type = "close_by_market"
                return True
            else:
                return False
