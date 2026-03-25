"""
Resolves day + round to prices/trades CSV paths.
Usage: from data_finder import find_data_files
"""

import os
import sys
import glob

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def find_data_files(day, round_num="0"):
    round_dir = os.path.join(DATA_DIR, f"round{round_num}")
    prices_path = os.path.join(round_dir, f"prices_round_{round_num}_day_{day}.csv")
    trades_path = os.path.join(round_dir, f"trades_round_{round_num}_day_{day}.csv")

    if not os.path.exists(prices_path):
        available = glob.glob(os.path.join(round_dir, "prices_*.csv"))
        days = [f.split("day_")[1].replace(".csv", "") for f in available]
        print(f"No data for day {day} in round {round_num}.")
        if days:
            print(f"Available days: {', '.join(sorted(days))}")
        sys.exit(1)

    if not os.path.exists(trades_path):
        print(f"Trades file not found: {trades_path}")
        sys.exit(1)

    return prices_path, trades_path
