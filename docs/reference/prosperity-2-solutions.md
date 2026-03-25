# IMC Prosperity 2 (2024) -- Comprehensive Strategy Guide

9,000+ teams competed over 15 days (5 rounds of 3 days each). Currency: SeaShells.

## Key Source Repositories and Writeups

| Source | Rank | Link |
|--------|------|------|
| **Team Linear Utility** | 2nd globally (3,501,647 seashells) | [GitHub](https://github.com/ericcccsliu/imc-prosperity-2) |
| **jmerle** | 9th globally | [GitHub](https://github.com/jmerle/imc-prosperity-2) |
| **pe049395** | 13th globally | [GitHub](https://github.com/pe049395/IMC-Prosperity-2024) |
| **hochfilzer** | 42nd globally | [GitHub](https://github.com/hochfilzer/prosperity2) |
| **AcreixYuan** | N/A | [GitHub](https://github.com/AcreixYuan/IMC-Prosperity-2) |
| **David Teather** | ~381st globally | [Blog](https://dteather.com/blogs/imc-prosperity-2/) / [Medium](https://medium.com/@davidteather/imc-prosperity-2-b1c94b1ebba8) |
| **gabsens (Manual rounds)** | N/A | [GitHub](https://github.com/gabsens/IMC-Prosperity-2-Manual) |

**Tools**: [Backtester (prosperity2bt)](https://pypi.org/project/prosperity2bt/) | [Visualizer](https://jmerle.github.io/imc-prosperity-2-visualizer/)

---

## ROUND 1: AMETHYSTS and STARFRUIT

### AMETHYSTS (Position Limit: 20)

- **Fair value**: Fixed at exactly **10,000 seashells** (never deviated)
- **Strategy**: Pure market making around 10,000
  - **Market taking**: Buy any asks below 10,000; sell into any bids above 10,000
  - **Market making**: Place bid orders slightly below 10,000 and ask orders slightly above 10,000, with an "edge" parameter optimized via grid search
  - **Position clearing**: Execute zero-EV trades to approach zero position when near limits, freeing capacity for profitable trades (~3% improvement per 2nd-place team)
  - **Soft/hard liquidation**: Tiered liquidation at less-than-usual prices when positions approached the limit boundary
- **Result** (Linear Utility): ~16k seashells from amethysts alone

### STARFRUIT (Position Limit: 20)

- **Fair value**: Slowly random-walking, relatively stable locally, slightly mean-reverting
- **Strategy**: Market making around an estimated fair price
  - **Fair price estimation**: Rolling average of mid-price over last `n` timestamps (parameter optimized via backtest)
  - **Key insight** (Linear Utility): The market maker bot's mid-price was less noisy than the overall mid-price -- identifying the large-volume market maker's quotes and using its mid as fair value was crucial
  - **Alternative**: "Popular mid-price" (max-volume bid + max-volume ask) / 2 as proxy for fair value
  - **Linear regression**: Some teams tried time-delayed regression on lagged prices; results were mixed
- **Result** (Linear Utility): Ranked 3rd globally in Round 1, 34,498 seashells

### Round 1 Manual: Bid Selection

- Select two bid prices between 900-1000
- Optimal bids (via grid search over 10M simulations): **952 and 978**

---

## ROUND 2: ORCHIDS

- **Strategy**: Cross-exchange statistical arbitrage
  - Orchids tradeable on local exchange AND South Archipelago via a "conversion" mechanism (subject to import tariffs, shipping costs)
  - **Profit formula**: `(local sell price - south exit price - shipping cost - import tariff) * execution probability`
  - Place large sell orders locally at profitable levels, then buy from South Archipelago via conversion
  - **Sell price formula**: `foreign_ask_price - 2`
- **Short selling approach** (jmerle, 9th): Continuously short-sell to position limit at profitable conversion prices, then immediately reposition
- **Environmental data**: Sunlight, humidity were available but no predictive value found -- purely arbitrage-based dominated
- **Backtested profit** (jmerle): ~109,000 seashells

### Round 2 Manual: Currency Arbitrage

- Arbitrage route: seashells -> pizza slices -> wasabi roots -> seashells -> pizza slices -> seashells
- Optimal profit: ~113,938 seashells (found by iterating all possible conversion chains)

---

## ROUND 3: GIFT_BASKET, CHOCOLATE, STRAWBERRIES, ROSES

### Basket Composition

**GIFT_BASKET** = 4 CHOCOLATE + 6 STRAWBERRIES + 1 ROSES

### Core Strategy: Spread / ETF Arbitrage

- **Spread**: `GIFT_BASKET_price - (4 * CHOCOLATE + 6 * STRAWBERRIES + 1 * ROSES)`
- **Key observation**: Spread oscillated around a mean of ~**370 seashells**

**Approach 1 -- Hardcoded thresholds:**
- Go long on baskets when spread drops below threshold; short when above
- Grid search over historical data for optimal entry/exit thresholds
- Projected PnL: ~120k seashells

**Approach 2 -- Adaptive z-score (Linear Utility, top approach):**
- `z-score = (spread - hardcoded_mean) / rolling_window_stdev`
- Hardcoded mean at ~370; short rolling window for stdev
- Small window caused z-score to spike when local volatility dropped, coinciding with price reversals
- Sell spreads when z-score > threshold; buy when z-score < -threshold
- Projected PnL: ~135k; Actual: ~111k seashells

**Approach 3 -- Basket-only trading (pe049395, 13th):**
- Only traded GIFT_BASKET itself (not components) to reduce transaction costs and slippage
- Used market orders "deep into the order book, accepting slippage" at extremes

**Common pitfall**: Trading individual components (especially ROSES) led to losses for many teams

### Round 3 Manual: Treasure Map

- Base reward 7,500 per tile; Individual = Base * Multiplier / (1 + Number of hunters)
- Optimal picks: Tiles I26 and H29 (game-theory based, anticipating other teams)

---

## ROUND 4: COCONUT and COCONUT_COUPON

### Product Details

- **COCONUT_COUPON**: European call option on COCONUT
- **Strike**: 10,000 | **Expiry**: 250 days | **Underlying**: ~10,000 (near ATM)
- **Position limits**: 300 coconuts / 600 coupons

### Black-Scholes Strategy

1. **Implied volatility**: Back out IV from market prices; IV oscillated around ~**16%**
2. **Mean reversion on IV**: Trade coupon when IV deviated from ~16%
3. **Fair value**: BS theoretical price with mean IV vs market price
4. **Delta hedging**: Delta ~0.53 per coupon
   - At max coupon position (600), needed ~318 coconuts to hedge, but only 300 limit -- accepted residual delta exposure (~18 delta units)
5. **Alternative**: Some teams assumed constant IV and simply compared model price to market price

### Performance

- **Backtested profit** (jmerle): ~420,000 seashells
- **Linear Utility**: 145k actual, but dropped to 26th place due to unlucky delta losses

### Easter Egg

- Coconut price data was a **near-exact match** of Prosperity 1 coconut data, with a **beta of 1.25**
- Discovered during Round 4; became key to Round 5 multi-million profits

---

## ROUND 5: All Products

### Critical Discovery: Cross-Year Data Mapping

The breakthrough separating top 4 teams from everyone else:

- **Prosperity 1 Diving Gear returns** (x ~3) predicted **ROSES** with **R^2 = 0.99**
- **Prosperity 1 Coconut data** (x 1.25) predicted **COCONUT** with **R^2 = 0.99**
- Top teams could know future prices with near-certainty

### Trader Signal Analysis (Bot Behavior)

| Signal | Action |
|--------|--------|
| Vladimir sells CHOCOLATE to Remy | Go **long** CHOCOLATE |
| Remy sells CHOCOLATE to Vladimir | Go **short** CHOCOLATE |
| Rihanna sells ROSES to Vinnie | Go **short** ROSES |
| Vinnie sells ROSES to Rihanna | Go **long** ROSES |

### Final Round Strategy Summary

- **AMETHYSTS**: Market making at 10,000
- **STARFRUIT**: Market making around popular mid-price
- **ORCHIDS**: Inter-archipelago arbitrage
- **GIFT_BASKET / STRAWBERRIES**: Threshold-based directional trading
- **COCONUT**: Directional trading using Prosperity 1 data (beta = 1.25)
- **COCONUT_COUPON**: Black-Scholes expected value trading
- **ROSES**: Directional trading using Prosperity 1 diving gear data (multiplier ~3)
- **CHOCOLATE**: Bot signal-based directional trading

---

## Key Infrastructure Used by Top Teams

1. **Custom backtester**: Replicated environment locally, matched orders against orderbook
2. **Dashboard/Visualizer**: Synchronized visualization across all metrics
3. **Grid search**: Systematic parameter optimization
4. **Monte Carlo simulation**: Data augmentation to prevent overfitting (13th-place team)
5. **Dynamic programming**: Optimized trading given volume constraints, spread costs, position limits (Linear Utility)
