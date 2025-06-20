from datetime import timedelta
import pandas as pd

from trading_2.testing.close_position_order_rule import ClosePositionOrderRule
from trading_2.testing.condition_signals import ConditionSignal
from trading_2.testing.process_trade_state import BaseProcessTrade
from trading_2.testing.test_service import TestService, Trade


class Test:
    def __init__(self, data_file: str, start_time: str, end_time: str):
        self.df = pd.read_csv(data_file, parse_dates=["timestamp"])
        self.df.set_index("timestamp", inplace=True)
        self.start_time = pd.Timestamp(start_time)
        self.end_time = pd.Timestamp(end_time)

    @staticmethod
    def check(conditions: list[ConditionSignal], current_row: pd.Series, history: dict, direction: str) -> bool:
        return all(condition.check_condition(current_row, history, direction) for condition in conditions)

    def _build_history(self, time: pd.Timestamp, delta_map: dict) -> dict:
        return {
            label: self.df.loc[time - delta]
            for label, delta in delta_map.items()
            if (time - delta) in self.df.index
        }

    def _should_open_trade(self, conditions, current_row, history, direction) -> bool:
        return self.check(conditions, current_row, history, direction)

    def _run_delay_phase(self, start_time, end_time, trade, process_trade_obj, direction, trades_results, **kwargs):
        while start_time <= trade.end_delay_period and start_time <= end_time:
            if not process_trade_obj.process_trade_state(self.df.loc[start_time], direction, trade, **kwargs):
                trades_results.calc_trade_result(self.df.loc[start_time], direction, trade)
                return start_time + timedelta(hours=4)
            start_time += timedelta(hours=4)
        return start_time

    def _run_main_phase(self, start_time, end_time, trade, process_trade_obj, direction,
                        trades_results, close_lose_position, close_profit_position, time_close_check, **kwargs):
        while start_time <= end_time:
            if not process_trade_obj.process_trade_state(
                self.df.loc[start_time],
                direction,
                trade,
                close_lose_position,
                close_profit_position,
                time_close_check=time_close_check,
                **kwargs
            ):
                trades_results.calc_trade_result(self.df.loc[start_time], direction, trade)
                return start_time + timedelta(hours=4)
            start_time += timedelta(hours=4)
        return start_time

    def test(
        self,
        enter_conditions: list[ConditionSignal],
        deltas: dict,
        process_trade_obj: BaseProcessTrade,
        direction: str,
        trades_results: TestService,
        stop_position_rule: ClosePositionOrderRule = None,
        profit_position_rule: ClosePositionOrderRule = None,
        close_lose_position: ConditionSignal = None,
        close_profit_position: ConditionSignal = None,
        time_close_check=False,
        **kwargs
    ):
        delta_map = {label: timedelta(hours=hours) for label, hours in deltas.items()}
        start_time = self.start_time
        end_time = self.end_time

        impulse_id = 0
        trade_id = 2

        while start_time <= end_time:
            history = self._build_history(start_time, delta_map)
            if len(history) != len(delta_map):
                start_time += timedelta(hours=4)
                continue

            current_row = self.df.loc[start_time]
            if self._should_open_trade(enter_conditions, current_row, history, direction):
                trade = Trade(current_row, direction, stop_position_rule, profit_position_rule, self.df, history)

                if current_row["impulse_id"] == impulse_id:
                    trade.id = trade_id
                    trade_id += 1
                else:
                    impulse_id = current_row["impulse_id"]
                    trade_id = 2

                start_time += timedelta(hours=4)
                start_time = self._run_delay_phase(
                    start_time, end_time, trade, process_trade_obj, direction, trades_results, **kwargs
                )

                if start_time <= end_time:
                    start_time = self._run_main_phase(
                        start_time, end_time, trade, process_trade_obj, direction,
                        trades_results, close_lose_position, close_profit_position,
                        time_close_check, **kwargs
                    )
            else:
                start_time += timedelta(hours=4)
