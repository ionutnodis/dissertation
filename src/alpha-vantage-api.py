import requests
import pandas as pd
import os
import time
from io import StringIO
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def download_1min_intraday(symbol, api_key, months_back=24, output_dir="data"):
    """
    Download 1min intraday data month-by-month using the new 'month' parameter.
    """
    base_url = "https://www.alphavantage.co/query"
    os.makedirs(output_dir, exist_ok=True)
    all_data = []

    today = datetime.today().replace(day=1)
    for i in range(months_back):
        target_month = (today - timedelta(days=1)).replace(day=1)  # go back one month each iteration
        month_str = target_month.strftime("%Y-%m")
        print(f"🔄 Downloading {symbol} {month_str}...")
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "1min",
            "outputsize": "full",
            "month": month_str,
            "apikey": api_key,
            "datatype": "csv"
        }

        resp = requests.get(base_url, params=params)
        if resp.status_code == 200 and "timestamp" in resp.text:
            df = pd.read_csv(StringIO(resp.text))
            df["month"] = month_str
            all_data.append(df)
        else:
            print(f"⚠️ Failed: {month_str} – {resp.status_code}, {resp.text[:200]}")
        time.sleep(12)

        # decrement month
        today = target_month

    if not all_data:
        print("❌ No data downloaded.")
        return None

    df_full = pd.concat(all_data, ignore_index=True)
    df_full["timestamp"] = pd.to_datetime(df_full["timestamp"])
    df_full.sort_values("timestamp", inplace=True)
    df_full.set_index("timestamp", inplace=True)

    filename = f"{output_dir}/{symbol}_1min_{months_back}mo_{datetime.now():%Y%m%d_%H%M}.csv"
    df_full.to_csv(filename)
    print(f"✅ Saved to {filename}")
    return df_full

symbol = "AAPL"
api_key = os.getenv("API_KEY")
df = download_1min_intraday(symbol, api_key, months_back=24)