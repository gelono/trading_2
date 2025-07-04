from pprint import pprint
from trading_2.testing.close_position_order_rule import StopProfitOrderATR, StopOrderBehindExtremum
from trading_2.testing.condition_signals import WorkPeriodCrossMAEarly, ImpulsPeriodDirection, \
    WorkPeriodCrossMAWithDelay, WorkPeriodCrossMALate, StrategicPeriodDirection, WorkPeriodCloseReverse, \
    ProfitByMomentum, WorkPeriodVolumeSignalOrMACrossLate, WorkPeriodVolumeSignal, WorkPeriodKnifeFilter, \
    WorkPeriodCrossMAEarlyOrLate, WorkPeriodExtremumToMAFilter, StrategicPeriodFilter, WorkPeriodStochasticEnterExit
from trading_2.testing.process_trade_state import BaseProcessTrade
from trading_2.testing.test_class import Test
from trading_2.testing.test_service import TestService

coin = "algo"
test_data = f"/home/oleg/PycharmProjects/Trading/trading_2/processing_data/csv/{coin}_hourly_with_4h_1d_1w_with_sma_4years.csv"

base_process_trade = BaseProcessTrade()
test_service = TestService()

limit = test_service.operational_history_period
deltas_dict = {f"prev_{i}h": i for i in range(4, limit * 4 + 4, 4)}

work_period_cross_MA_early = WorkPeriodCrossMAEarly()
work_period_cross_MA_late = WorkPeriodCrossMALate()
work_period_cross_MA_with_delay = WorkPeriodCrossMAWithDelay()
work_period_close_reverse = WorkPeriodCloseReverse()
work_period_volume_signal = WorkPeriodVolumeSignal(test_service.volume_coefficient)
work_period_volume_signal_or_ma_cross_late = WorkPeriodVolumeSignalOrMACrossLate(test_service.volume_coefficient)
work_period_cross_MA_early_or_late = WorkPeriodCrossMAEarlyOrLate()
work_period_stochastic_enter_exit = WorkPeriodStochasticEnterExit()

impuls_period_direction = ImpulsPeriodDirection()
work_period_knife_filter = WorkPeriodKnifeFilter()
strategic_period_direction = StrategicPeriodDirection()
strategic_period_filter = StrategicPeriodFilter()
work_period_extremum_to_ma_filter = WorkPeriodExtremumToMAFilter()

profit_position_rule_atr = StopProfitOrderATR()
stop_position_rule_atr = StopProfitOrderATR()
stop_position_rule_behind_extremum = StopOrderBehindExtremum()
close_profit_by_momentum = ProfitByMomentum()
close_profit_by_stochastic = WorkPeriodStochasticEnterExit()


list_enter_conditions = [work_period_cross_MA_early_or_late, impuls_period_direction, strategic_period_filter]

# test = Test(test_data, "2021-09-30 03:00:00", "2023-06-30 03:00:00")
test = Test(test_data, "2021-09-30 03:00:00", "2025-06-25 03:00:00")

test.test(list_enter_conditions, deltas_dict, base_process_trade, "buy", test_service, stop_position_rule=stop_position_rule_behind_extremum,
          profit_position_rule=profit_position_rule_atr, close_lose_position=None, close_profit_position=None, time_close_check=False,
          use_breakeven=True, add_position=False)

test.test(list_enter_conditions, deltas_dict, base_process_trade, "sell", test_service, stop_position_rule=stop_position_rule_behind_extremum,
          profit_position_rule=profit_position_rule_atr, close_lose_position=None, close_profit_position=None, time_close_check=False,
          use_breakeven=True, add_position=False)

sorted_results = sorted(test_service.total_results, key=lambda x: x["enter_date"])
pprint(sorted_results)

test_service.plot_cumulative_results(
    filter_conditions=[
        {
            "direction": "buy",
            "day_id": {"op": "lte", "value": 7},
            "weekday_1d": {"op": "in", "value": [2, 3, 4, 5, 6]}
        },
        {
            "direction": "sell",
            "day_id": {"op": "lte", "value": 7},
            "weekday_1d": {"op": "in", "value": [2, 3, 4, 5, 6]}
        }
    ],
    show_individual=False
)
