# Project Paradise IMC Prosperity 4 Toolkit

Shared infrastructure for IMC Prosperity 4, built and maintained by [Project Paradise](https://project-paradise.co.uk) — a student community working on mathematical modelling competitions and projects together.

This toolkit is open for everyone to use, modify, and share. If you're interested in quant, ML or mathematical modelling more broadly and want to learn by building things with others, [come join the community](https://project-paradise.co.uk).

## Setup

```bash
pip install -e .
```

## Usage

### Backtest a strategy

```bash
# Run on all round 0 days
./backtest.sh strategies/example.py 0

# Run on a specific day
./backtest.sh strategies/example.py 0--2

# Open in visualizer after
./backtest.sh strategies/example.py 0 --vis
```

### Bundle for submission

```bash
./submit.sh strategies/my_strat.py
# Output: submissions/my_strat.py (upload to prosperity.imc.com)
```

### Research tools

```bash
# Visualize price/trades/LOB for a day
python3 research/visualize.py -1        # day -1, round 0
python3 research/visualize.py -2 1      # day -2, round 1

# Trade impact analysis
python3 research/trade_impact.py -1

# Analyze submission/backtest logs
python3 research/analyze_logs.py backtests/my_run.log
```

### Parse submission logs into data

```bash
# Convert official submission logs into backtester-compatible CSVs
python3 backtester/parse_submission_logs.py path/to/log.log <round> <day>
```

## Writing a strategy

Copy `strategies/example.py` and implement your `Trader.run()` method. The logger in `strategies/logger.py` is automatically inlined by `submit.sh`.
