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
LOCATION_BINS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
LOCATION_LABELS = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
SIG_THRESHOLD = 1.65


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


def _fmt_impact(mean_val, se_val, n):
    if n < 2 or se_val == 0:
        marker = " "
    elif abs(mean_val / se_val) >= SIG_THRESHOLD:
        marker = "*"
    else:
        marker = " "
    return f"{mean_val:>+7.2f}{marker}"


def _print_group(label, subset, label_width=8):
    n = len(subset)
    print(f"{label:>{label_width}} {n:>5}", end="")
    for h in HORIZONS:
        col = f"impact_{h}"
        vals = subset[col].dropna()
        if len(vals) == 0:
            print(f" {'n/a':>8}", end="")
            continue
        mean_val = vals.mean()
        se_val = vals.std() / np.sqrt(len(vals)) if len(vals) > 1 else 0
        print(f" {_fmt_impact(mean_val, se_val, len(vals))}", end="")
    print()


def print_impact_by_quantity(impacts, product):
    print(f"\n{'='*60}")
    print(f"  {product} — Impact by Trade Size")
    print(f"{'='*60}")
    print(f"{'Qty':>8} {'Count':>5}", end="")
    for h in HORIZONS:
        print(f" {'t+'+str(h):>8}", end="")
    print()
    print("-" * 55)

    for qty in sorted(impacts["quantity"].unique()):
        subset = impacts[impacts["quantity"] == qty]
        _print_group(str(int(qty)), subset)

    print("-" * 55)
    _print_group("ALL", impacts)


def print_impact_by_location(impacts, product):
    print(f"\n{'='*60}")
    print(f"  {product} — Impact by Price Location")
    print(f"  (0.0 = running low, 1.0 = running high)")
    print(f"{'='*60}")

    impacts = impacts.copy()
    impacts["loc_bin"] = pd.cut(
        impacts["price_location"], bins=LOCATION_BINS,
        labels=LOCATION_LABELS, include_lowest=True,
    )

    print(f"{'Loc':>8} {'Count':>5}", end="")
    for h in HORIZONS:
        print(f" {'t+'+str(h):>8}", end="")
    print()
    print("-" * 55)

    for label in LOCATION_LABELS:
        subset = impacts[impacts["loc_bin"] == label]
        if len(subset) == 0:
            continue
        _print_group(label, subset)


def print_impact_crosstab(impacts, product):
    print(f"\n{'='*60}")
    print(f"  {product} — Quantity x Location (t+20 impact)")
    print(f"  (* = significant at 90%)")
    print(f"{'='*60}")

    impacts = impacts.copy()
    impacts["loc_bin"] = pd.cut(
        impacts["price_location"], bins=LOCATION_BINS,
        labels=LOCATION_LABELS, include_lowest=True,
    )

    quantities = sorted(impacts["quantity"].unique())
    active_locs = [l for l in LOCATION_LABELS
                   if len(impacts[impacts["loc_bin"] == l]) > 0]

    print(f"{'Qty':>5}", end="")
    for loc in active_locs:
        print(f" {loc:>12}", end="")
    print()
    print("-" * (5 + 13 * len(active_locs)))

    for qty in quantities:
        print(f"{int(qty):>5}", end="")
        for loc in active_locs:
            cell = impacts[(impacts["quantity"] == qty) & (impacts["loc_bin"] == loc)]
            if len(cell) == 0:
                print(f" {'---':>12}", end="")
                continue
            vals = cell["impact_20"].dropna()
            if len(vals) == 0:
                print(f" {'---':>12}", end="")
                continue
            mean_val = vals.mean()
            se_val = vals.std() / np.sqrt(len(vals)) if len(vals) > 1 else 0
            sig = "*" if len(vals) > 1 and se_val > 0 and abs(mean_val / se_val) >= SIG_THRESHOLD else " "
            print(f" {mean_val:>+7.2f}{sig}({len(vals):>2})", end="")
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

    all_impacts = {}
    for product in prices["product"].unique():
        product_prices = prices[prices["product"] == product].sort_values("timestamp")
        product_trades = trades[trades["symbol"] == product].sort_values("timestamp")
        if product_trades.empty:
            continue

        impacts = compute_impacts(product_prices, product_trades)
        all_impacts[product] = impacts
        print_impact_by_quantity(impacts, product)
        print_impact_by_location(impacts, product)
        print_impact_crosstab(impacts, product)


if __name__ == "__main__":
    main()
