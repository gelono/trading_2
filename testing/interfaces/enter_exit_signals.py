from abc import ABC, abstractmethod
import pandas as pd
from trading_2.testing.test_service import TradeSetting, Trade


class ConditionSignal(ABC, TradeSetting):
    @abstractmethod
    def check_condition(self, current_row: pd.Series, history: dict, direction: str) -> bool:
        pass

    @abstractmethod
    def check_exit_condition(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> bool:
        pass
