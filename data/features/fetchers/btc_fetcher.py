import logging
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
from binance.spot import Spot
from dotenv import load_dotenv

# ---------------------
# Setup & Environment
# ---------------------
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance Spot Client
client = Spot(api_key=API_KEY, api_secret=API_SECRET)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------
# Fetch OHLCV Function
# ---------------------
def fetch_ohlcv(symbol="BTCUSDT", interval="4h", years=5):
    """
    Fetch historical OHLCV data for given symbol and save it as .parquet

    Params:
    - symbol (str): e.g. 'BTCUSDT'
    - interval (str): Binance interval string, e.g. '4h'
    - years (int): How many years of historical data to fetch

    Returns:
    - pd.DataFrame: Raw OHLCV DataFrame
    """
    # Calculate timestamps
    end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ts = int((datetime.now(timezone.utc) - timedelta(days=365 * years)).timestamp() * 1000)

    logging.info(f"⏳ Fetching {symbol} OHLCV data | Interval: {interval} | "
                 f"Start: {datetime.fromtimestamp(start_ts / 1000)} | End: {datetime.fromtimestamp(end_ts / 1000)}")

    # Fetching loop (pagination)
    klines = []
    while True:
        logging.info(f"Fetching data from: {datetime.fromtimestamp(start_ts / 1000)}")
        try:
            batch = client.klines(
                symbol=symbol,
                interval=interval,
                startTime=start_ts,
                endTime=end_ts,
                limit=1000
            )
        except Exception as e:
            logging.error(f"Failed to fetch data: {e}")
            break

        if not batch:
            break
        klines.extend(batch)
        if len(batch) < 1000:
            break
        start_ts = batch[-1][0] + 1  # move to next candle

    logging.info(f"✅ Fetched {len(klines)} candles")

    # Create DataFrame
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])

    # Drop unnecessary column
    df.drop(columns=["Ignore"], inplace=True)

    # Convert time columns
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
    df["Close Time"] = pd.to_datetime(df["Close Time"], unit="ms")
    df.set_index("Open Time", inplace=True)

    # Convert numeric columns
    float_cols = ["Open", "High", "Low", "Close", "Volume",
                  "Quote Asset Volume", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume"]
    df[float_cols] = df[float_cols].astype(float)

    # Save to parquet
    output_dir = "data/features/raw"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{symbol}_{interval}_ohlcv.parquet")
    df.to_parquet(output_path)
    logging.info(f"✅ Saved to {output_path}")

    return df

# ---------------------
# Run as Script
# ---------------------
if __name__ == "__main__":
    df = fetch_ohlcv()
    print(df.head())
