import pandas as pd
from trading_2.processing_data.create_dataset import add_aggregated_ohlcv
from trading_2.processing_data.process_dataset import add_sma_columns_from_csv

# from processing_data.create_dataset import add_aggregated_ohlcv
# from processing_data.process_dataset import add_sma_columns_from_csv

def main():
    df = pd.read_csv('/home/oleg/PycharmProjects/Trading/trading_2/data/history/algo_ohlcv_1h.csv')
    df_result = add_aggregated_ohlcv(df)
    df_result.to_csv('csv/hourly_with_4h_1d_1w.csv', index=False)

    df_with_sma = add_sma_columns_from_csv('csv/hourly_with_4h_1d_1w.csv', period=3, shift=3)
    df_with_sma.to_csv('csv/hourly_with_4h_1d_1w_with_sma.csv', index=False)


if __name__ == "__main__":
    main()
