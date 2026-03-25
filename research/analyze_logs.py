"""Analyze submission logs. Usage: python3 research/analyze_logs.py path/to/logs.log"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_log(path):
    if path.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.endswith('.log'):
                    return json.loads(z.read(name))
    with open(path) as f:
        return json.load(f)


def analyze_activities(data):
    lines = data['activitiesLog'].strip().split('\n')
    header = lines[0].split(';')
    rows = [line.split(';') for line in lines[1:]]

    products = sorted(set(r[2] for r in rows))
    last_ts = rows[-1][1]
    last_rows = [r for r in rows if r[1] == last_ts]

    print("=== FINAL PNL ===")
    total = 0
    for r in last_rows:
        pnl = float(r[-1])
        total += pnl
        print(f"  {r[2]}: {pnl:,.2f}")
    print(f"  TOTAL: {total:,.2f}")

    print(f"\n=== ACTIVITY SUMMARY ===")
    print(f"  Timestamps: {rows[0][1]} to {last_ts}")
    print(f"  Total rows: {len(rows)}")
    print(f"  Products: {products}")

    # Track PnL over time
    pnl_by_ts = {}
    for r in rows:
        ts = int(r[1])
        pnl_by_ts.setdefault(ts, 0)
        pnl_by_ts[ts] += float(r[-1])

    timestamps = sorted(pnl_by_ts.keys())
    quarter = len(timestamps) // 4
    print(f"\n=== PNL TRAJECTORY ===")
    for label, idx in [("25%", quarter), ("50%", 2*quarter), ("75%", 3*quarter), ("100%", -1)]:
        ts = timestamps[idx]
        print(f"  {label}: ts={ts}, pnl={pnl_by_ts[ts]:,.2f}")

    # Spread analysis from real exchange
    print(f"\n=== REAL EXCHANGE SPREADS ===")
    for prod in products:
        prod_rows = [r for r in rows if r[2] == prod]
        spreads = []
        for r in prod_rows:
            bid1 = r[3]
            ask1 = r[9]
            if bid1 and ask1:
                spreads.append(int(ask1) - int(bid1))
        if spreads:
            print(f"  {prod}: mean={sum(spreads)/len(spreads):.1f}, min={min(spreads)}, max={max(spreads)}")


def analyze_trades(data):
    trades = data['tradeHistory']
    print(f"\n=== TRADE ANALYSIS ===")
    print(f"  Total fills: {len(trades)}")

    by_sym = {}
    for t in trades:
        by_sym.setdefault(t['symbol'], []).append(t)

    for sym, ts in sorted(by_sym.items()):
        buys = [t for t in ts if t['buyer'] == 'SUBMISSION']
        sells = [t for t in ts if t['seller'] == 'SUBMISSION']
        buy_vol = sum(t['quantity'] for t in buys)
        sell_vol = sum(t['quantity'] for t in sells)
        buy_cost = sum(t['price'] * t['quantity'] for t in buys)
        sell_rev = sum(t['price'] * t['quantity'] for t in sells)

        avg_buy = buy_cost / buy_vol if buy_vol else 0
        avg_sell = sell_rev / sell_vol if sell_vol else 0

        prices = [t['price'] for t in ts]
        print(f"\n  {sym}:")
        print(f"    Buys:  {len(buys)} fills, {buy_vol} vol, avg price {avg_buy:,.1f}")
        print(f"    Sells: {len(sells)} fills, {sell_vol} vol, avg price {avg_sell:,.1f}")
        print(f"    Edge per unit: {avg_sell - avg_buy:,.1f}" if avg_buy and avg_sell else "")
        print(f"    Price range: {min(prices):,.1f} - {max(prices):,.1f}")
        print(f"    Net position change: {buy_vol - sell_vol:+d}")

        # Fill rate over time
        timestamps = sorted(set(t['timestamp'] for t in ts))
        if len(timestamps) >= 2:
            duration = timestamps[-1] - timestamps[0]
            print(f"    Time span: {timestamps[0]} - {timestamps[-1]} ({len(timestamps)} unique ts)")


def analyze_errors(data):
    logs = data['logs']
    errors = [l for l in logs if l['sandboxLog']]
    print(f"\n=== ERRORS/WARNINGS ===")
    print(f"  Limit violations: {len(errors)}")

    if errors:
        by_product = {}
        for e in errors:
            for line in e['sandboxLog'].strip().split('\n'):
                if 'exceeded limit' in line:
                    prod = line.split('product ')[1].split(' exceeded')[0]
                    by_product[prod] = by_product.get(prod, 0) + 1
        for prod, count in sorted(by_product.items()):
            print(f"    {prod}: {count} violations")


def analyze_orders(data):
    """Parse our logger output to see what we were quoting."""
    logs = data['logs']
    print(f"\n=== ORDER ANALYSIS (from logger) ===")

    order_counts = {}
    for entry in logs:
        ll = entry['lambdaLog']
        if not ll:
            continue
        try:
            parsed = json.loads(ll)
            orders_list = parsed[1]  # [[symbol, price, qty], ...]
            for o in orders_list:
                sym = o[0]
                order_counts.setdefault(sym, {'buy': 0, 'sell': 0, 'buy_prices': [], 'sell_prices': []})
                if o[2] > 0:
                    order_counts[sym]['buy'] += 1
                    order_counts[sym]['buy_prices'].append(o[1])
                else:
                    order_counts[sym]['sell'] += 1
                    order_counts[sym]['sell_prices'].append(o[1])
        except (json.JSONDecodeError, IndexError, TypeError):
            continue

    for sym, info in sorted(order_counts.items()):
        bp = info['buy_prices']
        sp = info['sell_prices']
        print(f"\n  {sym}:")
        print(f"    Buy orders sent: {info['buy']} (prices: {min(bp)}-{max(bp)}, mean {sum(bp)/len(bp):.0f})" if bp else f"    Buy orders: 0")
        print(f"    Sell orders sent: {info['sell']} (prices: {min(sp)}-{max(sp)}, mean {sum(sp)/len(sp):.0f})" if sp else f"    Sell orders: 0")
        if bp and sp:
            print(f"    Our avg spread: {sum(sp)/len(sp) - sum(bp)/len(bp):.1f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 research/analyze_logs.py <path_to_log>")
        sys.exit(1)

    data = load_log(sys.argv[1])
    analyze_activities(data)
    analyze_trades(data)
    analyze_errors(data)
    analyze_orders(data)


if __name__ == "__main__":
    main()
