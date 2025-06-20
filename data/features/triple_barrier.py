# triple_barrier.py

import pandas as pd
import numpy as np
import logging


def triple_barrier_labels(df, pt=0.03, sl=0.02, horizon=12):
    """Assign labels using the triple barrier method.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least a ``Close`` column.
    pt : float, optional
        Profit-taking threshold, by default 0.03 (3%).
    sl : float, optional
        Stop-loss threshold, by default 0.02 (2%).
    horizon : int, optional
        Number of future bars to look ahead, by default 12.
    """

    logging.info(
        f"🏷️ Applying triple barrier labels (PT={pt * 100}%, "
        f"SL={sl * 100}%, Horizon={horizon} bars)..."
    )

    df = df.copy()
    close = df["Close"].values

    # Initialize labels with NaN so that rows without sufficient
    # future data are removed after labeling
    labels = np.full(len(df), np.nan)

    for i in range(len(close) - horizon):
        entry_price = close[i]
        upper_barrier = entry_price * (1 + pt)
        lower_barrier = entry_price * (1 - sl)

        # Look ahead to determine which barrier is hit first
        future_prices = close[i + 1 : i + 1 + horizon]

        hit_label = 0
        for price in future_prices:
            if price >= upper_barrier:
                hit_label = 1  # Profit
                break
            if price <= lower_barrier:
                hit_label = -1  # Loss
                break

        labels[i] = hit_label

    df["label"] = labels
    df.dropna(inplace=True)
    return df
