from backtester.datamodel import Order, OrderDepth, TradingState
from strategies.logger import Logger

logger = Logger()


class Trader:
    def run(self, state: TradingState):
        orders = {}

        for product, order_depth in state.order_depths.items():
            product_orders = []

            best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
            best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None

            if best_ask and best_bid:
                mid = (best_ask + best_bid) / 2
                product_orders.append(Order(product, int(mid - 1), 5))
                product_orders.append(Order(product, int(mid + 1), -5))
                logger.print(f"{product}: mid={mid:.0f}, bidding {int(mid-1)}, asking {int(mid+1)}")

            orders[product] = product_orders

        conversions = 0
        trader_data = state.traderData or ""
        logger.flush(state, orders, conversions, trader_data)
        return orders, conversions, trader_data
