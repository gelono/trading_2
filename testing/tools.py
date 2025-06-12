from datetime import timedelta
from typing import Dict
import pandas as pd

from testing.condition_signal import ConditionSignal, CheckSignal, WorkPeriodCrossMA, ImpulsPeriodDirection
from testing.enter_signals import EnterSignal, BaseEnterSignal
from testing.proceed_delay import ProceedDelay, BaseProceedDelay, TradeSetting, Trade


# from trading_2.testing.enter_signals import EnterSignal, BaseEnterSignal
# from trading_2.testing.proceed_delay import ProceedDelay, BaseProceedDelay


class Test:
    def __init__(self, data_file: str, start_time: str):
        self.df = pd.read_csv(data_file, parse_dates=["timestamp"])
        self.df.set_index("timestamp", inplace=True)
        self.start_time = pd.Timestamp(start_time)

    # def test(self, enter_signal: EnterSignal, proceed_delay_obj: ProceedDelay, direction: str, **kwargs):
    def test(self, conditions: list[ConditionSignal], deltas: dict, proceed_delay_obj: ProceedDelay, direction: str, **kwargs):
        start_time = self.start_time
        df = self.df
        check_signal = CheckSignal()

        # Преобразуем часы в timedelta
        delta_map: Dict[str, timedelta] = {
            label: timedelta(hours=hours)
            for label, hours in deltas.items()
        }

        while start_time <= df.index[-1]:
            history = {label: df.loc[start_time - delta] for label, delta in delta_map.items()
                       if (start_time - delta) in df.index}

            if len(history) != len(delta_map):
                start_time += timedelta(hours=4)
                continue

            kwargs["history"] = history
            # is_open_trade = enter_signal.signal(df.loc[start_time], direction, **kwargs)
            is_open_trade = check_signal.check(conditions, df.loc[start_time], history, direction)
            if is_open_trade:
                trade = Trade(df.loc[start_time], direction)
                start_time += timedelta(hours=4)
                delay_is_in_process = True
                while delay_is_in_process and start_time <= trade.end_delay_period:
                    delay_is_in_process = proceed_delay_obj.proceed_delay(df.loc[start_time], direction, trade, **kwargs)
                    start_time += timedelta(hours=4)
                    if not delay_is_in_process:
                        break
            else:
                start_time += timedelta(hours=4)


test_data = "/home/oleg/PycharmProjects/Trading/trading_2/processing_data/csv/hourly_with_4h_1d_1w_with_sma.csv"
test = Test(test_data, "2024-06-05 03:00:00")
# base_enter_signal = BaseEnterSignal()
# trade_settings = TradeSetting()
base_proceed_delay = BaseProceedDelay()
deltas_dict = {"prev_4h": 4}
work_period_cross_MA = WorkPeriodCrossMA()
impuls_period_direction = ImpulsPeriodDirection()
list_conditions = [work_period_cross_MA, impuls_period_direction]
test.test(list_conditions, deltas_dict, base_proceed_delay, "buy")
