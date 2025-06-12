from abc import ABC, abstractmethod

import pandas as pd


class ConditionSignal(ABC):
    @abstractmethod
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        pass


class CheckSignal:
    @staticmethod
    def check(conditions: list[ConditionSignal], current_row: pd.Series, history: dict, direction: str) -> bool:
        result = [condition.check_condition(current_row, history, direction) for condition in conditions]
        return  all(result)


class WorkPeriodCrossMA(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        prev_4h = history.get("prev_4h")
        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                current_row["close_4h"] < current_row["sma_4h"] and
                prev_4h["close_4h"] >= prev_4h["sma_4h"]
            )
        else:
            return (
                current_row["close_4h"] > current_row["sma_4h"] and
                prev_4h["close_4h"] <= prev_4h["sma_4h"]
            )


class ImpulsPeriodDirection(ConditionSignal):
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        if direction == "buy":
            return current_row["close_1d"] > current_row["sma_1d"]
        else:
            return current_row["close_1d"] < current_row["sma_1d"]
