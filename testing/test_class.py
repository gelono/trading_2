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

    @staticmethod
    def _use_breakeven(direction, trade, df, start_time):
        if direction == "buy":
            if df.loc[start_time - timedelta(hours=4)]["close_4h"] > trade.open_price:
                trade.stop_price = trade.open_price
        else:
            if df.loc[start_time - timedelta(hours=4)]["close_4h"] < trade.open_price:
                trade.stop_price = trade.open_price

    @staticmethod
    def _add_position(direction, trade, df, start_time):
        if direction == "buy":
            if df.loc[start_time - timedelta(hours=4)]["close_4h"] > trade.open_price:
                prev_price = df.loc[start_time - timedelta(hours=4)]["close_4h"]
                trade.open_price = 2 / (1 / trade.open_price + 1 / prev_price)
                trade.added_position = True
        else:
            if df.loc[start_time - timedelta(hours=4)]["close_4h"] < trade.open_price:
                prev_price = df.loc[start_time - timedelta(hours=4)]["close_4h"]
                trade.open_price = 2 / (1 / trade.open_price + 1 / prev_price)
                trade.added_position = True

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
        use_breakeven=False,
        add_position=False,
        **kwargs
    ):
        delta_map = {label: timedelta(hours=hours) for label, hours in deltas.items()}
        start_time = self.start_time
        end_time = self.end_time
        df = self.df

        impulse_id = 0
        trade_id = 2

        while start_time <= end_time: #df.index[-1]:
            history = {label: df.loc[start_time - delta] for label, delta in delta_map.items()
                       if (start_time - delta) in df.index}

            if len(history) != len(delta_map):
                start_time += timedelta(hours=4)
                continue

            is_open_trade = self.check(enter_conditions, df.loc[start_time], history, direction)
            if is_open_trade:
                trade = Trade(df.loc[start_time], direction, stop_position_rule, profit_position_rule, df, history)
                if df.loc[start_time]["impulse_id"] == impulse_id:
                    trade.id = trade_id
                    trade_id += 1
                else:
                    impulse_id = df.loc[start_time]["impulse_id"]
                    trade_id = 2

                start_time += timedelta(hours=4)
                delay_is_in_process = True
                while delay_is_in_process and start_time <= trade.end_delay_period and start_time <= end_time:
                    delay_is_in_process = process_trade_obj.process_trade_state(df.loc[start_time],
                                   direction, trade, **kwargs)

                    if not delay_is_in_process:
                        trades_results.calc_trade_result(df.loc[start_time], direction, trade)
                        is_open_trade = False
                        start_time += timedelta(hours=4)
                    else:
                        start_time += timedelta(hours=4)

                if is_open_trade:
                    if use_breakeven:
                        self._use_breakeven(direction, trade, df, start_time)
                    if add_position:
                        self._add_position(direction, trade, df, start_time)

                    while is_open_trade and start_time <= end_time: #df.index[-1]:
                        is_open_trade = process_trade_obj.process_trade_state(df.loc[start_time],
                                   direction, trade, close_lose_position, close_profit_position,
                                    time_close_check=time_close_check, **kwargs)
                        if not is_open_trade:
                            trades_results.calc_trade_result(df.loc[start_time], direction, trade)
                            start_time += timedelta(hours=4)
                        else:
                            start_time += timedelta(hours=4)
            else:
                start_time += timedelta(hours=4)
