import pandas as pd
import matplotlib.pyplot as plt
from trading_2.processing_data.create_dataset import add_aggregated_ohlcv
from trading_2.processing_data.process_dataset import add_sma_columns_from_csv


def analyze_impulse_durations(df: pd.DataFrame) -> pd.Series:
    """
    Возвращает Series, где индекс — это длина импульса (в днях),
    а значения — количество таких импульсов.
    """
    if "impulse_id" not in df.columns or "day_id" not in df.columns:
        raise ValueError("Требуются колонки 'impulse_id' и 'day_id'")

    # Удалим строки без идентификатора импульса
    df_valid = df.dropna(subset=["impulse_id", "day_id"])

    # Группируем по импульсам и считаем уникальные day_id в каждом импульсе
    impulse_lengths = df_valid.groupby("impulse_id")["day_id"].nunique()

    # Строим гистограмму: сколько импульсов каждой длины
    length_distribution = impulse_lengths.value_counts().sort_index()

    return length_distribution


def plot_impulse_duration_distribution(df: pd.DataFrame) -> None:
    """
    Строит гистограмму количества импульсов различной длительности (в днях).
    """
    if "impulse_id" not in df.columns or "day_id" not in df.columns:
        print("⛔ Требуются колонки 'impulse_id' и 'day_id'")
        return

    # Группируем по импульсам и считаем уникальные day_id
    impulse_lengths = df.dropna(subset=["impulse_id", "day_id"]).groupby("impulse_id")["day_id"].nunique()

    # Получаем распределение по длине
    length_distribution = impulse_lengths.value_counts().sort_index()

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.bar(length_distribution.index, length_distribution.values, width=0.6, color="skyblue", edgecolor="black")
    plt.xlabel("Длительность импульса (в днях)")
    plt.ylabel("Количество импульсов")
    plt.title("Распределение длительности импульсов")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(length_distribution.index)
    plt.tight_layout()
    plt.show()


def main():
    coin = "tao"
    df = pd.read_csv(f'/home/oleg/PycharmProjects/Trading/trading_2/data/history/{coin}_ohlcv_1h_2years.csv')
    df_result = add_aggregated_ohlcv(df)
    df_result.to_csv(f'csv/{coin}_hourly_with_4h_1d_1w_2years.csv', index=False)

    df_with_sma = add_sma_columns_from_csv(f'csv/{coin}_hourly_with_4h_1d_1w_2years.csv', period=3, shift=3, fill=False)
    plot_impulse_duration_distribution(df_with_sma)

    # print("Распределение длин импульсов (в днях):")
    # print(distribution)

if __name__ == "__main__":
    main()