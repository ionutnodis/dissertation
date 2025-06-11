#Function to get 1-minute BTC data from Binance

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def get_binance_1min_klines(symbol: str, start_time: str, end_time: str):
    """
    Fetches 1-minute kline (candlestick) data from Binance between start and end times.
    
    Args:
        symbol: str — e.g. "BTCUSDT"
        start_time: str — e.g. "2023-06-01 04:00:00"
        end_time: str — e.g. "2025-05-30 20:00:00"
    
    Returns:
        DataFrame with timestamp, open, high, low, close, volume
    """
    base_url = "https://api.binance.com/api/v3/klines"
    interval = "1m"
    limit = 1000
    df_list = []

    start_ts = int(pd.Timestamp(start_time).timestamp() * 1000)
    end_ts = int(pd.Timestamp(end_time).timestamp() * 1000)

    while start_ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ts,
            "endTime": min(start_ts + limit * 60 * 1000, end_ts),
            "limit": limit
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text[:100]}")
            break

        data = response.json()
        if not data:
            break

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["open_time"], unit='ms')
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].astype({
            "open": float, "high": float, "low": float, "close": float, "volume": float
        })
        df.set_index("timestamp", inplace=True)
        df_list.append(df)

        # move start timestamp forward
        start_ts = int(df.index[-1].timestamp() * 1000) + 60_000
        time.sleep(0.2)  # Binance rate limit buffer

    if df_list:
        full_df = pd.concat(df_list)
        full_df.sort_index(inplace=True)
        return full_df
    else:
        return pd.DataFrame()

# === Usage ===
start = "2023-06-01 04:00:00"
end = "2025-05-30 20:00:00"
btc_df = get_binance_1min_klines("BTCUSDT", start, end)

# Optional: Save to CSV
btc_df.to_csv("BTCUSDT_1min_matched_to_TSLA.csv")