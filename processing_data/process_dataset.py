import pandas as pd

def add_sma_columns_from_csv(csv_path, period=3, shift=3):
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Список интервалов и соответствующих колонок закрытия
    intervals = {
        '4h': 'close_4h',
        '1d': 'close_1d',
        '1w': 'close_1w'
    }

    for interval, close_col in intervals.items():
        if close_col in df.columns:
            sma_col = f'sma_{interval}'
            close_4h_series = df[close_col].dropna()
            rolling_avg = close_4h_series.rolling(window=period).mean().shift(shift)
            df[sma_col] = rolling_avg.reindex(df.index)
            if sma_col in ["sma_1d", "sma_1w"]:
                df[sma_col] = df[sma_col].ffill()

    df["close_1d"] = df["close_1d"].ffill()
    df["close_1w"] = df["close_1w"].ffill()

    df.reset_index(inplace=True)
    return df
