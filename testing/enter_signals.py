from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd


class EnterSignal(ABC):
    VALID_DIRECTIONS = {"buy", "sell"}

    def __init__(self, deltas: Dict[str, int]):
        """
        :param deltas: dictionary like {"prev_4h": 4, "prev_12h": 12}
        """
        self.deltas = deltas

    def signal(self, row: pd.Series, direction: str, *args, **kwargs) -> bool:
        """
        :param row: one row from pd.Dataframe
        :param direction: "buy" or "sell"
        """
        direction = direction if direction in self.VALID_DIRECTIONS else "buy"
        return self._signal(row, direction, *args, **kwargs)

    @abstractmethod
    def _signal(self, row: pd.Series, direction: str, *args, **kwargs) -> bool:
        pass


class BaseEnterSignal(EnterSignal):
    def _signal(self, row: pd.Series, direction: str, *args, **kwargs) -> bool:
        history: Dict[str, pd.Series] = kwargs.get("history", {})
        prev_4h = history.get("prev_4h")
        if prev_4h is None:
            raise ValueError("Missing 'prev_4h' in history")

        if direction == "buy":
            return (
                row["close_1d"] > row["sma_1d"] and
                row["close_4h"] < row["sma_4h"] and
                prev_4h["close_4h"] >= prev_4h["sma_4h"]
            )
        else:
            return (
                row["close_1d"] < row["sma_1d"] and
                row["close_4h"] > row["sma_4h"] and
                prev_4h["close_4h"] <= prev_4h["sma_4h"]
            )
