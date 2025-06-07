from abc import ABC, abstractmethod
from datetime import timedelta

import pandas as pd


class TradeSetting:
    stop_size: float = 3.0
    delay_period: int = 24 # hours amount


class Trade(TradeSetting):
    def __init__(self, row: pd.Series, direction: str):
        self.open_price = row["close_4h"]
        self.end_delay_period = pd.Timestamp(row["timestamp"]) + timedelta(hours=self.delay_period)
        self.stop_price = self.open_price - self.stop_size if direction == "buy" else self.open_price + self.stop_size


class ProceedDelay(ABC):
    @abstractmethod
    def proceed_delay(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs):
        pass


class BaseProceedDelay(ProceedDelay):
    def proceed_delay(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs):
        pass
        # stop filled check
        # profit filled check

        return # state of delay process (bool)