# IMC Prosperity 3 (2025) -- Comprehensive Strategy Guide

12,000+ teams competed over 15 days (5 rounds of 3 days each). Currency: SeaShells. By Round 5, 15 tradeable products.

## Key Source Repositories and Writeups

| Source | Rank | Link |
|--------|------|------|
| **TimoDiehm** | 2nd globally | [GitHub](https://github.com/TimoDiehm/imc-prosperity-3) |
| **chrispyroberts** | 7th globally / 1st USA | [GitHub](https://github.com/chrispyroberts/imc-prosperity-3) |
| **Alpha Animals (CarterT27)** | 9th globally / 2nd USA (1,190,077) | [GitHub](https://github.com/CarterT27/imc-prosperity-3) |
| **v3natio** | ~200th / 1st Spain | [GitHub](https://github.com/v3natio/prosperity-imc-2025) |
| **nicolassinott** | N/A | [GitHub](https://github.com/nicolassinott/IMC_Prosperity) |

**Tools**: [Backtester](https://github.com/jmerle/imc-prosperity-3-backtester) | [Visualizer](https://jmerle.github.io/imc-prosperity-3-visualizer/) | [Leaderboard](https://jmerle.github.io/imc-prosperity-leaderboard/)

**Blog Posts**: [Martin Oravec (Medium)](https://medium.com/@oravec.martin01/imc-prosperity-3-be859180f133) | [Matius Chong (Medium)](https://medium.com/@matius_chong/imc-prosperity-3-challenge-2025-2af2a7a4132b) | [venatio blog](https://v3natio.github.io/posts/prosperity-imc-2025/)

---

## ROUND 1: Market Making (RAINFOREST_RESIN, KELP, SQUID_INK)

### RAINFOREST_RESIN (Position Limit: 50)

- **Fair value**: Fixed at exactly **10,000** (+/- 4 SeaShells)
- **Strategy**: Pure market making around the fixed price
  - Take any favorable trades: buy below 10,000, sell above 10,000
  - Place passive quotes slightly better than existing book liquidity
  - Flatten inventory at exactly 10,000 when skewed
- **Contribution**: ~39,000 SeaShells/round consistently

### KELP (Position Limit: 50)

- **Fair value**: Slow random walk with minor movements
- **Strategy**: Market making using **WallMid** (midpoint of best bid/ask from large market makers) as fair price
  - Identify large bids/asks from consistent market makers, track their mid-price
  - Place limit orders around calculated mid with configurable spreads
- **Contribution**: ~5,000 SeaShells/round

### SQUID_INK (Position Limit: 50)

- **Key characteristic**: Tighter bid-ask spread relative to average movement, with occasional sharp price jumps -- pure market making had high variance

**Strategy A (2nd place team): Bot behavior detection**
- Identified a bot ("Olivia") that bought 15 lots at the daily low and sold 15 at the daily high
- Tracked daily running minimum/maximum
- Positioned ahead of anticipated reversions when trades at extrema detected

**Strategy B (9th place team): Volatility spike mean-reversion**
- Detected price movements exceeding **3 standard deviations** from a **10-timestamp rolling window**
- Took positions opposite to detected spikes
- Position management rules limiting exposure time

- **Contribution**: ~8,000 SeaShells/round

### Round 1 Manual: Currency Arbitrage

- Given a conversion matrix between currencies
- Find 5 trades to maximize profit
- Approach: BFS/graph algorithms to find optimal conversion chains
- Max profit achievable: ~8.9%

---

## ROUND 2: ETF/Basket Arbitrage (CROISSANTS, JAMS, DJEMBES, PICNIC_BASKET1, PICNIC_BASKET2)

### Basket Compositions

- **PICNIC_BASKET1** = 6 Croissants + 3 Jams + 1 Djembe
- **PICNIC_BASKET2** = 4 Croissants + 2 Jams

### Core Strategy: Synthetic Basket Arbitrage

- Calculate synthetic fair value of each basket from component midpoints
- Compare live basket mid-price to synthetic value
- Trade the spread when it diverges

### Key Parameters (2nd place team)

- **Fixed threshold model** with entry/exit points (~+/- 50)
- **Dynamic Olivia-informed adjustments**: If Olivia detected as short, long entry moved to -80, short entry to +20
- **Hedge ratio**: 50% for constituent exposure
- **Exit**: When spread crosses zero (adjusted for informed signal)

### Z-Score Approaches (other teams)

- Hard-coded the mean from historical data
- Short rolling window for standard deviation
- When **z-score > 20**: short basket, long constituents
- When **z-score < -20**: long basket, short constituents
- Alternative: `z-score = (EMA_short - EMA_long) / Std_Dev_long`

### Component Mean-Reversion (supplementary)

- 100-tick rolling window on each component
- When mid deviates by ~2 standard deviations from recent mean, lean the other way
- Position-aware sizing

**Contribution**: 40,000-60,000 SeaShells/round (baskets) + ~20,000 (constituents)

### Round 2 Manual: Container Game Theory

- 10 containers, open up to 2 (second costs 50,000 SeaShells)
- Each container has a multiplier; inhabitants also choose
- Strategy: Rank by expected value, favor "off-peak" choices with decent multipliers and low expected popularity

---

## ROUND 3: Options Trading (VOLCANIC_ROCK, VOLCANIC_ROCK_VOUCHER_*)

### Product Details

- **Volcanic Rock**: Underlying, trades around ~10,000
- **Vouchers**: European call options with strikes at 9500, 9750, 10000, 10250, 10500
- **Time to expiry**: Starts at 7 days, decays to ~2 days by final round
- **Position limits**: 400 (Volcanic Rock), 200 (each voucher)

### Black-Scholes Pricing Strategy

- Assumed **zero risk-free rate**
- Inverted market mid-prices to extract **implied volatility** per strike
- Maintained a **rolling volatility window**

### Volatility Smile

- Observed persistent volatility smile: IV higher away from ATM
- Fitted a **quadratic parabola** to IV across strikes
- Mapped each option to moneyness (time-scaled log-moneyness)
- Blended global curve with per-strike rolling IV estimate to stabilize noise

### IV Scalping (primary profit driver)

- Detrended IV to isolate moneyness-independent deviations
- Scalped IV mean reversion across strike levels
- Dynamically expanded across strikes, adjusting thresholds

### Delta Hedging

- Summed option deltas across portfolio
- Rebalanced underlying whenever book delta moved outside a small band

### Gamma Scalping

- Positive expected value: gains from underlying price movements outweighed theta decay
- Bought options and rehedged resulting deltas
- Maintained moderate mean reversion position in underlying and deepest ITM call

### Greeks Used

- **Delta**: Sensitivity to underlying price -- guides hedging
- **Vega**: Sensitivity to volatility -- gauges IV signal strength
- **Gamma**: Rate of delta change -- drives gamma scalping profit

---

## ROUND 4: Cross-Market Arbitrage (MAGNIFICENT_MACARONS)

### Product Details

- **Position limit**: 75 units
- **Conversion limit**: 10 units per timestep
- Fair value depends on: sunlight hours, sugar prices, shipping costs, tariffs, storage capacity

### Trading Mechanics

- Trade on local island exchange (order book) OR externally at fixed bid/ask (adjusted for fees)
- Import/export fees, transportation costs, and tariffs apply to conversions

### Key Strategy: Regime-Based Cross-Market Arbitrage

**Normal Sunlight Regime:**
- Two-way arbitrage between local and foreign markets
- Buy locally, sell abroad when local < foreign (after fees), and vice versa

**Low Sunlight Regime:**
- Switch to accumulation strategy
- Aggressively build long positions
- Avoid exports

### Hidden Detail

- A taker bot aggressively filled orders offered at attractive prices relative to a hidden "fair value"
- Understanding this hidden bot was key to optimizing order placement

### Round 4 Manual: Suitcase Challenge

- Calculate Nash equilibrium across all suitcases
- Determine if opening two suitcases was profitable based on Nash EV exceeding cost
- Model human behavior using Discord post-analysis data

---

## ROUND 5: Counterparty Identification (All Products + Trader IDs Revealed)

### Key Change

- Historical trader IDs made public
- Could directly identify which trades came from specific bots

### Olivia Copy-Trading Strategy

- **Identification method**: Calculate "percentage of good trades" per counterparty in rolling windows
- Olivia consistently bought before price increases and sold before drops
- Detection: Suspiciously precise timing on buy/sell relative to mid-price

### Implementation

- **Squid Ink & Croissants**: Used Olivia's trades as regime signals
  - Bullish signal: Match her buys
  - Bearish signal: Match her sells
- **Direct ID checking** replaced indirect heuristics, eliminating false positives

### Macaron Revision

- Removed sunlight index dependence
- Shifted to pure statistical arbitrage throughout entire trading day

### All Other Strategies Maintained

- Market making: Kelp, Rainforest Resin
- Statistical arbitrage: Picnic Baskets
- Black-Scholes: Volcanic Rock Vouchers

---

## Key Takeaways for Prosperity 4

1. **Stability over peak performance**: Avoid overfitting to backtests; robustness wins
2. **Bot behavior detection**: Identifying informed traders (like "Olivia") is crucial
3. **Basket arbitrage**: Proper hedge ratios and spread mean-reversion are reliable profit sources
4. **Options**: Correct Black-Scholes with volatility smile fitting; delta hedging is essential
5. **Cross-year data**: Check if Prosperity 3 data maps to Prosperity 4 products (beta/scaling factors)
6. **WallMid**: Using large market maker quotes as fair value proxy beats simple mid-price
7. **Lambda memory**: Algorithms exceeding **100MB** on AWS Lambda had variables wiped on restart -- keep state lean
