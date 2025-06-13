from pprint import pprint

from trading_2.testing.condition_signal import WorkPeriodCrossMAEarly, ImpulsPeriodDirection, \
    WorkPeriodCrossMAWithDelay, WorkPeriodCrossMALate
from trading_2.testing.process_trade_state import BaseProcessTrade
from trading_2.testing.test_class import Test
from trading_2.testing.trade_services import TradesResults

test_data = "/home/oleg/PycharmProjects/Trading/trading_2/processing_data/csv/hourly_with_4h_1d_1w_with_sma.csv"

base_process_trade = BaseProcessTrade()
trades_results = TradesResults()
deltas_dict = {
    "prev_4h": 4,
    "prev_8h": 8,
}

work_period_cross_MA_early = WorkPeriodCrossMAEarly()
work_period_cross_MA_late = WorkPeriodCrossMALate()
work_period_cross_MA_with_delay = WorkPeriodCrossMAWithDelay()
impuls_period_direction = ImpulsPeriodDirection()


list_enter_conditions = [work_period_cross_MA_late, impuls_period_direction]

test = Test(test_data, "2024-06-12 03:00:00")
test.test(list_enter_conditions, deltas_dict, base_process_trade, "buy", trades_results)
test.test(list_enter_conditions, deltas_dict, base_process_trade, "sell", trades_results)

# sorted_results = sorted(trades_results.total_results, key=lambda x: x["enter_date"])
# pprint(sorted_results)

trades_results.plot_cumulative_results(
    filter_conditions=[
        {"direction": "buy", "trade_id": 1},
        {"direction": "buy", "trade_id": 2},
        {"direction": "buy", "trade_id": 3},
        # {"direction": "buy", "trade_id": 4},
        #
        {"direction": "sell", "trade_id": 1},
        {"direction": "sell", "trade_id": 2},
        {"direction": "sell", "trade_id": 3},
        # {"direction": "sell", "trade_id": 4},
    ],
    show_individual=False
)
