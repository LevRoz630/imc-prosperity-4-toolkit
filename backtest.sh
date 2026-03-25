#!/usr/bin/env bash
# Usage: ./backtest.sh strategies/my_strat.py 0
#        ./backtest.sh strategies/my_strat.py 0--2    (round 0, day -2 only)
#        ./backtest.sh strategies/my_strat.py 0 --vis  (open visualizer)
set -e
python3 -m backtester "$@"
