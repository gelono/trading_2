from abc import ABC, abstractmethod
from trading_2.testing.test_service import TradeSetting


class ClosePositionOrderRule(ABC, TradeSetting):
    @abstractmethod
    def get_stop_price(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_profit_price(self, *args, **kwargs):
        pass
