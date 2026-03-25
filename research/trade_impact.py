"""
Trade impact analysis — detects informed trader patterns.
Usage: python research/trade_impact.py <day> [round]
Example: python research/trade_impact.py -1
"""

import sys
import os
import pandas as pd
import numpy as np
from data_finder import find_data_files

HORIZONS = [1, 5, 10, 20]


def compute_impacts(product_prices, product_trades):
    timestamps = product_prices["timestamp"].values
    mids = product_prices["mid_price"].values

    results = []
    for _, trade in product_trades.iterrows():
        ts = trade["timestamp"]
        idx = np.searchsorted(timestamps, ts)
        if idx >= len(timestamps):
            continue

        mid_at_trade = np.interp(ts, timestamps, mids)
        side = 1 if trade["price"] >= mid_at_trade else -1

        running_min = mids[:idx + 1].min()
        running_max = mids[:idx + 1].max()
        running_range = running_max - running_min
        if running_range > 0:
            price_location = (mid_at_trade - running_min) / running_range
        else:
            price_location = 0.5

        row = {
            "timestamp": ts,
            "side": side,
            "quantity": trade["quantity"],
            "price_location": price_location,
        }

        for h in HORIZONS:
            future_idx = idx + h
            if future_idx < len(mids):
                signed_return = side * (mids[future_idx] - mid_at_trade)
                row[f"impact_{h}"] = signed_return
            else:
                row[f"impact_{h}"] = np.nan

        results.append(row)

    return pd.DataFrame(results)


def print_impact_by_quantity(impacts, product):
    print(f"\n{'='*60}")
    print(f"  {product} — Impact by Trade Size")
    print(f"{'='*60}")
    print(f"{'Qty':>5} {'Count':>6}", end="")
    for h in HORIZONS:
        print(f" {'t+'+str(h):>8}", end="")
    print()
    print("-" * 50)

    for qty in sorted(impacts["quantity"].unique()):
        subset = impacts[impacts["quantity"] == qty]
        print(f"{qty:>5} {len(subset):>6}", end="")
        for h in HORIZONS:
            col = f"impact_{h}"
            mean_val = subset[col].mean()
            print(f" {mean_val:>+8.2f}", end="")
        print()

    total = impacts
    print("-" * 50)
    print(f"{'ALL':>5} {len(total):>6}", end="")
    for h in HORIZONS:
        print(f" {total[f'impact_{h}'].mean():>+8.2f}", end="")
    print()


def print_impact_by_location(impacts, product):
    print(f"\n{'='*60}")
    print(f"  {product} — Impact by Price Location")
    print(f"  (0.0 = running low, 1.0 = running high)")
    print(f"{'='*60}")

    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    labels = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
    impacts["loc_bin"] = pd.cut(impacts["price_location"], bins=bins, labels=labels, include_lowest=True)

    print(f"{'Loc':>8} {'Count':>6}", end="")
    for h in HORIZONS:
        print(f" {'t+'+str(h):>8}", end="")
    print()
    print("-" * 55)

    for label in labels:
        subset = impacts[impacts["loc_bin"] == label]
        if len(subset) == 0:
            continue
        print(f"{label:>8} {len(subset):>6}", end="")
        for h in HORIZONS:
            mean_val = subset[f"impact_{h}"].mean()
            print(f" {mean_val:>+8.2f}", end="")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python research/trade_impact.py <day> [round]")
        print("Example: python research/trade_impact.py -1")
        sys.exit(1)

    day = sys.argv[1]
    round_num = sys.argv[2] if len(sys.argv) > 2 else "0"
    prices_path, trades_path = find_data_files(day, round_num)

    prices = pd.read_csv(prices_path, sep=";")
    trades = pd.read_csv(trades_path, sep=";")
    day_label = str(prices["day"].iloc[0])
    print(f"Trade Impact Analysis — Day {day_label}")

    for product in prices["product"].unique():
        product_prices = prices[prices["product"] == product].sort_values("timestamp")
        product_trades = trades[trades["symbol"] == product].sort_values("timestamp")
        if product_trades.empty:
            continue

        impacts = compute_impacts(product_prices, product_trades)
        print_impact_by_quantity(impacts, product)
        print_impact_by_location(impacts, product)


if __name__ == "__main__":
    main()
