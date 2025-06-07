from abc import ABC, abstractmethod
import pandas as pd


class TradeSetting:
    def __init__(self, stop_size):
        self.stop_size = stop_size


class ProceedDelay(ABC):
    def __init__(self, setting: TradeSetting):
        self.settings = setting

    @abstractmethod
    def proceed_delay(self, row: pd.Series, direction: str, *args, **kwargs):
        pass


class BaseProceedDelay(ProceedDelay):
    def proceed_delay(self, row: pd.Series, direction: str, *args, **kwargs):
        used_data = {}
        open_price = row["close_4h"]
        stop_size = self.settings.stop_size
        stop_price = open_price - stop_size if direction == "buy" else open_price + stop_size

        

        return used_data
