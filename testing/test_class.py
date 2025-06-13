from datetime import timedelta
from typing import Dict
import pandas as pd

from trading_2.testing.condition_signal import ConditionSignal, CheckSignal
from trading_2.testing.process_trade_state import BaseProcessTrade
from trading_2.testing.trade_services import TradesResults, Trade


class Test:
    def __init__(self, data_file: str, start_time: str):
        self.df = pd.read_csv(data_file, parse_dates=["timestamp"])
        self.df.set_index("timestamp", inplace=True)
        self.start_time = pd.Timestamp(start_time)

    def test(
            self,
            enter_conditions: list[ConditionSignal],
            deltas: dict,
            process_trade_obj: BaseProcessTrade,
            direction: str,
            trades_results: TradesResults,
            **kwargs
    ):
        start_time = self.start_time
        df = self.df
        check_signal = CheckSignal()

        # Преобразуем часы в timedelta
        delta_map: Dict[str, timedelta] = {
            label: timedelta(hours=hours)
            for label, hours in deltas.items()
        }
        impulse_id = 0
        trade_id = 2
        while start_time <= df.index[-1]:
            history = {label: df.loc[start_time - delta] for label, delta in delta_map.items()
                       if (start_time - delta) in df.index}

            if len(history) != len(delta_map):
                start_time += timedelta(hours=4)
                continue

            kwargs["history"] = history

            is_open_trade = check_signal.check(enter_conditions, df.loc[start_time], history, direction)
            if is_open_trade:
                trade = Trade(df.loc[start_time], direction)
                if df.loc[start_time]["impulse_id"] == impulse_id:
                    trade.id = trade_id
                    trade_id += 1
                else:
                    impulse_id = df.loc[start_time]["impulse_id"]
                    trade_id = 2

                start_time += timedelta(hours=4)
                delay_is_in_process = True
                while delay_is_in_process and start_time <= trade.end_delay_period and start_time <= df.index[-1]:
                    delay_is_in_process, exit_type = process_trade_obj.process_trade_state(df.loc[start_time],
                                   direction, trade, close_lose_position=None, close_profit_position=None, **kwargs)

                    if not delay_is_in_process:
                        trades_results.calc_trade_result(df.loc[start_time], direction, trade, exit_type)
                        is_open_trade = False
                        start_time += timedelta(hours=4)
                    else:
                        start_time += timedelta(hours=4)

                if is_open_trade:
                    while is_open_trade and start_time <= df.index[-1]:
                        is_open_trade, exit_type = process_trade_obj.process_trade_state(df.loc[start_time],
                                   direction, trade, close_lose_position=None, close_profit_position=None, **kwargs) # add close_lose_position, close_profit_position
                        if not is_open_trade:
                            trades_results.calc_trade_result(df.loc[start_time], direction, trade, exit_type)
                            start_time += timedelta(hours=4)
                        else:
                            start_time += timedelta(hours=4)
            else:
                start_time += timedelta(hours=4)
