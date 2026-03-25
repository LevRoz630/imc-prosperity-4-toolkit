"""
Round data visualizer.
Usage: python research/visualize.py <day> [round]
Example: python research/visualize.py -1
Output: research/plots/{product}_day_{day}.png
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from data_finder import find_data_files


def infer_trade_side(trade_price, mid_price):
    if trade_price >= mid_price:
        return "buy"
    return "sell"


def plot_product(product_prices, product_trades, product_name, day_label, output_dir):
    fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True)
    fig.suptitle(f"{product_name}  (day {day_label})", fontsize=14, fontweight="bold")
    timestamps = product_prices["timestamp"]

    # --- Panel 1: Price + Trades ---
    ax = axes[0]
    ax.plot(timestamps, product_prices["mid_price"], color="black", linewidth=0.8, label="Mid")
    ax.fill_between(
        timestamps,
        product_prices["bid_price_1"],
        product_prices["ask_price_1"],
        alpha=0.15,
        color="steelblue",
        label="Best bid/ask",
    )

    if not product_trades.empty:
        mid_at_trade = np.interp(product_trades["timestamp"], timestamps, product_prices["mid_price"])
        sides = [
            infer_trade_side(p, m)
            for p, m in zip(product_trades["price"], mid_at_trade)
        ]
        buys = product_trades[[s == "buy" for s in sides]]
        sells = product_trades[[s == "sell" for s in sides]]

        ax.scatter(buys["timestamp"], buys["price"], marker="^", color="green", s=buys["quantity"] * 8, alpha=0.7, zorder=5)
        ax.scatter(sells["timestamp"], sells["price"], marker="v", color="red", s=sells["quantity"] * 8, alpha=0.7, zorder=5)

    price_min = product_prices["bid_price_1"].min()
    price_max = product_prices["ask_price_1"].max()
    price_margin = max((price_max - price_min) * 0.15, 1)
    ax.set_ylim(price_min - price_margin, price_max + price_margin)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.set_ylabel("Price")
    buy_patch = mpatches.Patch(color="green", label="Buy-side trade")
    sell_patch = mpatches.Patch(color="red", label="Sell-side trade")
    ax.legend(handles=[buy_patch, sell_patch], loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Panel 2: Spread ---
    ax = axes[1]
    spread = product_prices["ask_price_1"] - product_prices["bid_price_1"]
    ax.plot(timestamps, spread, color="purple", linewidth=0.8)
    ax.set_ylabel("Spread")
    ax.grid(True, alpha=0.3)

    # --- Panel 3: LOB Depth ---
    ax = axes[2]
    bid_cols = ["bid_volume_1", "bid_volume_2", "bid_volume_3"]
    ask_cols = ["ask_volume_1", "ask_volume_2", "ask_volume_3"]

    bid_volumes = product_prices[bid_cols].fillna(0).values
    ask_volumes = product_prices[ask_cols].fillna(0).values

    colors_bid = ["#2196F3", "#64B5F6", "#BBDEFB"]
    colors_ask = ["#F44336", "#E57373", "#FFCDD2"]

    bid_cumulative = np.zeros(len(timestamps))
    for i, col in enumerate(bid_cols):
        ax.fill_between(timestamps, -bid_cumulative - bid_volumes[:, i], -bid_cumulative, color=colors_bid[i], alpha=0.7, label=f"Bid L{i+1}")
        bid_cumulative += bid_volumes[:, i]

    ask_cumulative = np.zeros(len(timestamps))
    for i, col in enumerate(ask_cols):
        ax.fill_between(timestamps, ask_cumulative, ask_cumulative + ask_volumes[:, i], color=colors_ask[i], alpha=0.7, label=f"Ask L{i+1}")
        ask_cumulative += ask_volumes[:, i]

    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_ylabel("Volume")
    ax.set_xlabel("Timestamp")
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = os.path.join(output_dir, f"{product_name}_day_{day_label}.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python research/visualize.py <day> [round]")
        print("Example: python research/visualize.py -1")
        sys.exit(1)

    day = sys.argv[1]
    round_num = sys.argv[2] if len(sys.argv) > 2 else "0"
    prices_path, trades_path = find_data_files(day, round_num)

    output_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(output_dir, exist_ok=True)

    prices = pd.read_csv(prices_path, sep=";")
    trades = pd.read_csv(trades_path, sep=";")
    day_label = str(prices["day"].iloc[0])

    for product in prices["product"].unique():
        product_prices = prices[prices["product"] == product].sort_values("timestamp")
        product_trades = trades[trades["symbol"] == product].sort_values("timestamp") if "symbol" in trades.columns else pd.DataFrame()
        plot_product(product_prices, product_trades, product, day_label, output_dir)


if __name__ == "__main__":
    main()
