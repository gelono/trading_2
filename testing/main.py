from pprint import pprint
from trading_2.testing.close_position_order_rule import StopProfitOrderATR, StopOrderBehindExtremum
from trading_2.testing.condition_signals import WorkPeriodCrossMAEarly, ImpulsPeriodDirection, \
    WorkPeriodCrossMAWithDelay, WorkPeriodCrossMALate, StrategicPeriodDirection, WorkPeriodCloseReverse, \
    ProfitByMomentum, WorkPeriodVolumeSignalOrMACrossLate, WorkPeriodVolumeSignal, WorkPeriodKnifeFilter, \
    WorkPeriodCrossMAEarlyOrLate, WorkPeriodExtremumToMAFilter, StrategicPeriodFilter, LowATRFilter
from trading_2.testing.process_trade_state import BaseProcessTrade
from trading_2.testing.test_class import Test
from trading_2.testing.test_service import TestService

coin = "tao"
test_data = f"/home/oleg/PycharmProjects/Trading/trading_2/processing_data/csv/{coin}_hourly_with_4h_1d_1w_with_sma_2years.csv"

base_process_trade = BaseProcessTrade()
test_service = TestService()

limit = test_service.operational_history_period
day_limit = test_service.day_operational_history_for_atr_period

deltas_dict = {f"prev_{i}h": i for i in range(4, limit * 4 + 4, 4)}
day_deltas_dict = {f"prev_{i/24}D": i for i in range(24, day_limit * 24 + 24, 24)}

work_period_cross_MA_early = WorkPeriodCrossMAEarly()
work_period_cross_MA_late = WorkPeriodCrossMALate()
work_period_cross_MA_with_delay = WorkPeriodCrossMAWithDelay()
work_period_close_reverse = WorkPeriodCloseReverse()
work_period_volume_signal = WorkPeriodVolumeSignal(test_service.volume_coefficient)
work_period_volume_signal_or_ma_cross_late = WorkPeriodVolumeSignalOrMACrossLate(test_service.volume_coefficient)
work_period_cross_MA_early_or_late = WorkPeriodCrossMAEarlyOrLate()

impuls_period_direction = ImpulsPeriodDirection()
work_period_knife_filter = WorkPeriodKnifeFilter()
strategic_period_direction = StrategicPeriodDirection()
strategic_period_filter = StrategicPeriodFilter()
work_period_extremum_to_ma_filter = WorkPeriodExtremumToMAFilter()
low_atr_filter = LowATRFilter()

profit_position_rule = StopProfitOrderATR()
stop_position_rule = StopProfitOrderATR()
stop_position_rule_extremum = StopOrderBehindExtremum()
profit_by_momentum = ProfitByMomentum()


list_enter_conditions = [work_period_volume_signal_or_ma_cross_late, impuls_period_direction]

test = Test(test_data, "2023-06-11 23:00:00", "2025-06-10 23:00:00")

test.test(list_enter_conditions, deltas_dict, day_deltas_dict, base_process_trade, "buy", test_service, stop_position_rule=stop_position_rule_extremum,
          profit_position_rule=profit_position_rule, close_lose_position=None, close_profit_position=None, time_close_check=False)

test.test(list_enter_conditions, deltas_dict, day_deltas_dict, base_process_trade, "sell", test_service, stop_position_rule=stop_position_rule_extremum,
          profit_position_rule=profit_position_rule, close_lose_position=None, close_profit_position=None, time_close_check=False)

sorted_results = sorted(test_service.total_results, key=lambda x: x["enter_date"])
pprint(sorted_results)

test_service.plot_cumulative_results(
    filter_conditions=[
        {
            "direction": "buy",
            "day_id": {"op": "lte", "value": 10},
            # "weekday_1d": {"op": "in", "value": [2, 3, 4, 5, 6]}
            "weekday_1d": {"op": "in", "value": [0, 1, 2, 3, 4]}
        },
        {
            "direction": "sell",
            "day_id": {"op": "lte", "value": 10},
            # "weekday_1d": {"op": "in", "value": [2, 3, 4, 5, 6]}
            "weekday_1d": {"op": "in", "value": [0, 1, 2, 3, 4]}
        }
    ],
    show_individual=False
)
