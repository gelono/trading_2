import pandas as pd

def add_aggregated_ohlcv(df_origin):
    df = df_origin.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Параметры агрегации: имя суффикса, частота, сдвиг для индекса, маска
    agg_configs = [
        ('4h', '4H', pd.Timedelta(hours=3), lambda idx: (idx.hour + 1) % 4 == 0),
        ('1d', '1D', pd.Timedelta(hours=23), lambda idx: idx.hour == 23),
        ('1w', '1W-MON', pd.Timedelta(days=6, hours=23), lambda idx: (idx.weekday == 6) & (idx.hour == 23)),
    ]

    df_combined = df.copy()

    for suffix, rule, shift, mask_func in agg_configs:
        df_resampled = df.resample(rule, label='left', closed='left').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

        df_resampled.columns = [f'{col}_{suffix}' for col in df_resampled.columns]
        df_resampled.index += shift

        df_combined = df_combined.merge(df_resampled, how='left', left_index=True, right_index=True)

        mask = mask_func(df_combined.index)
        for col in df_resampled.columns:
            df_combined.loc[~mask, col] = pd.NA

    df_combined.reset_index(inplace=True)
    return df_combined
