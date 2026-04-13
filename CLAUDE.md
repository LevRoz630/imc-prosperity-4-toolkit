# IMC Prosperity 4 Toolkit

Trading strategy backtesting framework for the IMC Prosperity 4 competition.

## Quick Reference

```bash
# Install
pip install -e .

# Backtest a strategy against round data
./backtest.sh strategies/my_strat.py 0          # all days in round 0
./backtest.sh strategies/my_strat.py 0--2       # specific day
./backtest.sh strategies/my_strat.py 0 --vis    # open in visualizer

# Bundle for submission
./submit.sh strategies/my_strat.py

# Research tools
python3 research/visualize.py -1                # visualize day -1
python3 research/trade_impact.py -1             # trade impact analysis
python3 research/analyze_logs.py backtests/*.log # analyze backtest logs
```

## Project Structure

- `backtester/` - Core engine: CLI (`__main__.py`), execution (`runner.py`), data models (`datamodel.py`), data loading (`data.py`)
- `strategies/` - User strategies. Each implements `Trader.run(state) -> (orders, conversions, trader_data)`
- `research/` - Analysis and visualization scripts (matplotlib/pandas)
- `data/` - Sample CSV data files by round
- `docs/reference/` - Past Prosperity solutions and strategy principles

## Key Conventions

- Strategies must define a `Trader` class with a `run(self, state: TradingState)` method
- `run()` returns a tuple: `(dict[str, list[Order]], int, str)` — orders by symbol, conversions, serialized trader data
- Prices and quantities are integers; timestamps are integer milliseconds
- Use `Logger` from `strategies/logger.py` for output (auto-inlined on submission)
- Position limits are enforced per product (e.g., 80 for EMERALDS, TOMATOES)
- `traderData` is a string — serialize/deserialize state yourself (JSON recommended)

## Domain Notes

- Order book: `buy_orders` (positive volumes) and `sell_orders` (negative volumes) in `OrderDepth`
- Positive quantity in `Order` = buy, negative = sell
- Strategy principles: re-tune don't rewrite, don't overfit, keep it simple, explain edge from first principles
