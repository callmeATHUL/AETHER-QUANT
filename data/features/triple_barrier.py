# triple_barrier.py

import pandas as pd
import numpy as np
import logging


def triple_barrier_labels(df, pt=0.03, sl=0.02, horizon=12):
	logging.info(f"🏷️ Applying triple barrier labels (PT={pt * 100}%, SL={sl * 100}%, Horizon={horizon} bars)...")
	
	df = df.copy()
	close = df['Close'].values
	labels = np.zeros(len(df))
	
	for i in range(len(close) - horizon):
		entry_price = close[i]
		upper_barrier = entry_price * (1 + pt)
		lower_barrier = entry_price * (1 - sl)
		
		# Future window
		future_prices = close[i + 1: i + 1 + horizon]
		
		hit_label = 0
		for price in future_prices:
			if price >= upper_barrier:
				hit_label = 1  # Profit
				break
			elif price <= lower_barrier:
				hit_label = -1  # Loss
				break
		labels[i] = hit_label
	
	df['label'] = labels
	df.dropna(inplace=True)
	return df
