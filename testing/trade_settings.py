class TradeSetting:
    taker_fee: float = 0.05
    maker_fee: float = 0.02

    stop_size: float = 2.0 # percent
    profit_size: float = 4.0 # percent
    stop_lookback_period: int = 6

    time_close_check: int = 24 # hours amount

    delay_period: int = 4 # hours amount
    operational_history_period: int = 30 # amount of rows
    day_operational_history_for_atr_period: int = 10

    percent_range_from_current_price_to_calc_atr_filter: float = 0.1

    atr_period: int = 18 # amount of 4h bars
    momentum_period: int = 2 # amount of 4h bars

    extremum_to_ma_filter: float = 0.02

    volume_coefficient: float = 1.75
    atr_coefficient_stop: float = 0.5 #0.75
    atr_coefficient_profit: float = 2.0 #1.75