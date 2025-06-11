import pandas as pd
import os
import joblib
import logging
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print(f"📍 Current Script Path: {os.path.abspath(__file__)}")
print(f"📁 Current Working Directory: {os.getcwd()}")


# Logging setup
logging.basicConfig(level=logging.INFO)


def load_features(path=None):
        if path is None:
                base = Path(__file__).resolve().parent / "processed"
                path = base / "BTCUSDT_4h_features.parquet"
        path = Path(path)
        if not path.exists():
                raise FileNotFoundError(f"Feature file not found at {path}")
        df = pd.read_parquet(path)
        logging.info(f"📦 Loaded feature data: {df.shape[0]} rows")
        return df


def prepare_data(df):
	# Add label (future 5-bar return binary)
	df["future_return_5"] = df["Close"].shift(-5) / df["Close"] - 1
	df["label"] = (df["future_return_5"] > 0).astype(int)
	df.dropna(inplace=True)
	
	# Select features
	features = ["rsi_14", "macd_hist", "atr_14", "bb_percent_b", "vwap"]
	X = df[features]
	y = df["label"]
	
	return train_test_split(X, y, test_size=0.2, shuffle=False)


def train_model(X_train, y_train):
	model = LGBMClassifier(n_estimators=200, random_state=42)
	model.fit(X_train, y_train)
	return model


def evaluate_model(model, X_test, y_test):
	preds = model.predict(X_test)
	acc = accuracy_score(y_test, preds)
	report = classification_report(y_test, preds)
	logging.info(f"✅ Accuracy: {acc:.4f}")
	print(report)


def save_model(model, name="models/AetherCore-1.pkl"):
	os.makedirs("models", exist_ok=True)
	joblib.dump(model, name)
	logging.info(f"✅ Model saved to {name}")


def run():
	df = load_features()
	X_train, X_test, y_train, y_test = prepare_data(df)
	model = train_model(X_train, y_train)
	evaluate_model(model, X_test, y_test)
	save_model(model)


if __name__ == "__main__":
	run()
