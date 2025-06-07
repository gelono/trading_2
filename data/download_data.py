import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time


def fetch_binance_ohlcv(symbol='BTC/USDT', timeframe='1h', days=10, filename='ohlcv_data.csv'):
    binance = ccxt.binance()
    since = binance.parse8601((datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S'))

    all_ohlcv = []
    limit = 100  # Максимум 1000 свечей за запрос (примерно 41.6 дня для 1h)

    while since < binance.milliseconds():
        print(f'Запрос данных с {binance.iso8601(since)}...')
        try:
            ohlcv = binance.fetch_ohlcv(symbol, timeframe, since, limit)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1  # Переход к следующему времени
            time.sleep(0.5)  # Уважение к лимитам API
        except Exception as e:
            print(f'Ошибка: {e}')
            time.sleep(5)

    # Преобразуем в DataFrame
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Сохраняем в CSV
    df.to_csv(filename, index=False)
    print(f'Данные сохранены в {filename}')


# Пример использования
# fetch_binance_ohlcv(symbol='ALGO/USDT', timeframe='1h', days=365, filename='history/algo_ohlcv_1h.csv')
