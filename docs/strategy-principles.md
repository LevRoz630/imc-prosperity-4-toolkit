# Strategy Principles

## Re-tune, don't rewrite

Carry strategies forward between rounds. The logic stays the same — re-optimize parameters on new data each round. Top P3 teams ran the same MM and arb strategies all 5 rounds, just re-ran grid searches when new data dropped.

## Don't overfit on backtests

A strategy that looks great in backtest but can't be explained is probably noise. Prioritize stable parameter regions over peak performance. If a small parameter shift kills your PnL, you're overfitting.

## Explain it with real behavior first

Before coding anything, explain why the edge exists in terms of actual market behavior. "The L2 resting orders are more honest than L1" is a reason. "This MA crossover happens to work on day -1" is not. If you can't explain why it should work from first principles, don't trade it.

## Keep it simple

Minimize parameters. A strategy with 2 knobs that you understand beats one with 10 that you don't. Complexity is where bugs and overfitting hide.
