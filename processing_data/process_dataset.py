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

    df = add_impulse_numbers(df)

    df.reset_index(inplace=True)
    return df


def add_impulse_numbers(df: pd.DataFrame, sma_col: str = "sma_1d", close_col: str = "close_1d") -> pd.DataFrame:
    df = df.copy()

    # Инициализация новой колонки
    df["impulse_id"] = pd.NA

    # Исключаем строки без значений
    valid_mask = df[sma_col].notna() & df[close_col].notna()
    df_valid = df[valid_mask].copy()

    # Считаем разницу между ценой и скользящей
    df_valid["above"] = df_valid[close_col] > df_valid[sma_col]

    # Сдвиг на 1 и сравнение — True, где произошел переход (пересечение)
    df_valid["crossover"] = df_valid["above"] != df_valid["above"].shift()

    # Начинаем нумерацию: каждое True означает новый импульс
    df_valid["impulse_id"] = df_valid["crossover"].cumsum().astype("Int64")

    # Объединяем с оригиналом
    df["impulse_id"] = df_valid["impulse_id"]

    return df
