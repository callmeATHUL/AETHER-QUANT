import logging
import os

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from dotenv import load_dotenv

from triple_barrier import triple_barrier_labels

# Load environment variables
load_dotenv()
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "4h")

# Configure logging
logging.basicConfig(level=logging.INFO)


def load_raw_data(symbol=SYMBOL, interval=INTERVAL):
	path = f"raw/{symbol}_{interval}_ohlcv.parquet"
	print("Looking for file at:", path)
	
	if not os.path.exists(path):
		raise FileNotFoundError(f"❌ Data not found: {path}")
	
	df = pd.read_parquet(path)
	logging.info(f"📦 Loaded raw data: {df.shape[0]} rows")
	validate_raw_data(df)
	return df

def validate_raw_data(df):
	required_columns = ["Open", "High", "Low", "Close", "Volume"]
	if df.empty:
		raise ValueError("❌ Raw data is empty")
	if not all(col in df.columns for col in required_columns):
		raise ValueError(f"❌ Raw data missing required columns: {required_columns}")


def add_indicators(df):
	logging.info("➕ Adding indicators...")
	df = df.copy()
	
	# VWAP: 24h rolling (6 candles of 4h = 24h)
	window = 6
	typical_price = (df['High'] + df['Low'] + df['Close']) / 3
	df['vwap'] = (typical_price * df['Volume']).rolling(window=window).sum() / df['Volume'].rolling(window=window).sum()
	
	# Momentum
	df['rsi_14'] = RSIIndicator(df['Close'], window=14).rsi()
	macd = MACD(df['Close'])
	df['macd_hist'] = macd.macd_diff()
	df['atr_14'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
	bb = BollingerBands(df['Close'], window=20)
	df['bb_percent_b'] = bb.bollinger_pband()
	df['sma_50'] = SMAIndicator(df['Close'], window=50).sma_indicator()
	df['ema_20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
	
	# Temporal
	if not isinstance(df.index, pd.DatetimeIndex):
		df.index = pd.to_datetime(df.index)
	df['hour'] = df.index.hour
	df['day_of_week'] = df.index.dayofweek  # Monday = 0
	
	return df


def clean_df(df):
	logging.info("🧹 Cleaning data...")
	df = df.copy()
	df = df.dropna()
	df = df.sort_index()
	return df


def save_features(df, symbol=SYMBOL, interval=INTERVAL):
	os.makedirs("processed", exist_ok=True)
	out_path = f"processed/{symbol}_{interval}_features.parquet"
	df.to_parquet(out_path)
	logging.info(f"✅ Saved feature data to {out_path}")


def run_pipeline():
	try:
		df = load_raw_data()
		df = add_indicators(df)
		df = clean_df(df)
		df = triple_barrier_labels(df, pt=0.03, sl=0.02, horizon=12)
		save_features(df)
	except Exception as e:
		logging.error(f"❌ Pipeline failed: {e}", exc_info=True)
		raise


if __name__ == "__main__":
	run_pipeline()
