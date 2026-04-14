from datamodel import OrderDepth, TradingState, Order
import json
import math


INTARIAN_PEPPER_ROOT = "INTARIAN_PEPPER_ROOT"
ASH_COATED_OSMIUM = "ASH_COATED_OSMIUM"

LONG = 1
NEUTRAL = 0
SHORT = -1

POS_LIMITS = {
    INTARIAN_PEPPER_ROOT: 80,
    ASH_COATED_OSMIUM: 80,
}

MEAN_REVERSION_CONFIG = {
    INTARIAN_PEPPER_ROOT: {
        "window": 5,
        "threshold": 0.40,
        "history_size": 250,
        "flatten_band": 0.05,
    }
}

STRATEGY_CONFIG = {
    INTARIAN_PEPPER_ROOT: {"type": "mean_reversion"},
    ASH_COATED_OSMIUM: {"type": "market_making_placeholder"},
}


class ProductTrader:
    def __init__(self, name, state, prints, new_trader_data):
        self.name = name
        self.state = state
        self.prints = prints
        self.new_trader_data = new_trader_data
        self.orders = []

        self.position_limit = POS_LIMITS.get(name, 0)
        self.initial_position = state.position.get(name, 0)

        self.last_trader_data = self.get_last_trader_data()
        self.mkt_buy_orders, self.mkt_sell_orders = self.get_order_depth()
        self.best_bid, self.best_ask = self.get_best_bid_ask()
        self.mid_price = self.get_mid_price()
        self.max_allowed_buy_volume, self.max_allowed_sell_volume = self.get_max_allowed_volume()

    def get_last_trader_data(self):
        try:
            if self.state.traderData:
                return json.loads(self.state.traderData)
        except Exception:
            pass
        return {}

    def get_order_depth(self):
        order_depth = self.state.order_depths.get(self.name, OrderDepth())
        buy_orders = {}
        sell_orders = {}

        try:
            buy_orders = {
                price: abs(volume)
                for price, volume in sorted(order_depth.buy_orders.items(), key=lambda item: item[0], reverse=True)
            }
        except Exception:
            pass

        try:
            sell_orders = {
                price: abs(volume)
                for price, volume in sorted(order_depth.sell_orders.items(), key=lambda item: item[0])
            }
        except Exception:
            pass

        return buy_orders, sell_orders

    def get_best_bid_ask(self):
        best_bid = max(self.mkt_buy_orders.keys()) if self.mkt_buy_orders else None
        best_ask = min(self.mkt_sell_orders.keys()) if self.mkt_sell_orders else None
        return best_bid, best_ask

    def get_mid_price(self):
        if self.best_bid is not None and self.best_ask is not None:
            return 0.5 * (self.best_bid + self.best_ask)
        if self.best_bid is not None:
            return float(self.best_bid)
        if self.best_ask is not None:
            return float(self.best_ask)
        return None

    def get_max_allowed_volume(self):
        max_allowed_buy_volume = self.position_limit - self.initial_position
        max_allowed_sell_volume = self.position_limit + self.initial_position
        return max_allowed_buy_volume, max_allowed_sell_volume

    def bid(self, price, volume):
        volume = max(0, min(int(volume), self.max_allowed_buy_volume))
        if volume <= 0:
            return
        self.orders.append(Order(self.name, int(price), volume))
        self.max_allowed_buy_volume -= volume

    def ask(self, price, volume):
        volume = max(0, min(int(volume), self.max_allowed_sell_volume))
        if volume <= 0:
            return
        self.orders.append(Order(self.name, int(price), -volume))
        self.max_allowed_sell_volume -= volume

    def log(self, key, value):
        group = self.prints.get(self.name, {})
        group[key] = value
        self.prints[self.name] = group

    def get_orders(self):
        return {self.name: self.orders}


class MeanReversionTrader(ProductTrader):
    def __init__(self, name, state, prints, new_trader_data, config):
        super().__init__(name, state, prints, new_trader_data)
        self.config = config
        self.history_key = f"{self.name}_mid_history"
        self.signal_key = f"{self.name}_signal"

    def update_history(self):
        history = self.last_trader_data.get(self.history_key, [])
        if self.mid_price is not None:
            history = history + [self.mid_price]
        history = history[-self.config["history_size"] :]
        self.new_trader_data[self.history_key] = history
        return history

    def get_signal(self, history):
        window = self.config["window"]
        if len(history) < window:
            previous_signal = self.last_trader_data.get(self.signal_key, NEUTRAL)
            self.new_trader_data[self.signal_key] = previous_signal
            return previous_signal, None, None, None

        window_prices = history[-window:]
        mean_price = sum(window_prices) / window
        variance = sum((price - mean_price) ** 2 for price in window_prices) / window
        std_price = math.sqrt(variance)

        previous_signal = self.last_trader_data.get(self.signal_key, NEUTRAL)
        if std_price <= 1e-9:
            signal = previous_signal
            zscore = 0.0
        else:
            zscore = (window_prices[-1] - mean_price) / std_price
            signal = previous_signal
            if zscore <= -self.config["threshold"]:
                signal = LONG
            elif zscore >= self.config["threshold"]:
                signal = SHORT
            elif abs(zscore) <= self.config["flatten_band"]:
                signal = NEUTRAL

        self.new_trader_data[self.signal_key] = signal
        return signal, zscore, mean_price, std_price

    def trade_to_target(self, target_position, fair_price):
        current_position = self.initial_position
        buy_needed = max(0, target_position - current_position)
        sell_needed = max(0, current_position - target_position)

        if buy_needed > 0:
            for ask_price, ask_volume in self.mkt_sell_orders.items():
                if ask_price > fair_price:
                    break
                trade_volume = min(buy_needed, ask_volume, self.max_allowed_buy_volume)
                self.bid(ask_price, trade_volume)
                buy_needed -= trade_volume
                if buy_needed <= 0:
                    break

            if buy_needed > 0 and self.best_bid is not None:
                passive_bid = min(self.best_bid + 1, int(math.floor(fair_price)))
                if self.best_ask is None or passive_bid < self.best_ask:
                    self.bid(passive_bid, buy_needed)

        if sell_needed > 0:
            for bid_price, bid_volume in self.mkt_buy_orders.items():
                if bid_price < fair_price:
                    break
                trade_volume = min(sell_needed, bid_volume, self.max_allowed_sell_volume)
                self.ask(bid_price, trade_volume)
                sell_needed -= trade_volume
                if sell_needed <= 0:
                    break

            if sell_needed > 0 and self.best_ask is not None:
                passive_ask = max(self.best_ask - 1, int(math.ceil(fair_price)))
                if self.best_bid is None or passive_ask > self.best_bid:
                    self.ask(passive_ask, sell_needed)

    def get_orders(self):
        history = self.update_history()
        signal, zscore, mean_price, std_price = self.get_signal(history)

        self.log("position", self.initial_position)
        self.log("mid", self.mid_price)
        self.log("signal", signal)
        self.log("zscore", None if zscore is None else round(zscore, 4))
        self.log("rolling_mean", None if mean_price is None else round(mean_price, 4))
        self.log("rolling_std", None if std_price is None else round(std_price, 4))

        if self.mid_price is None or mean_price is None:
            return {self.name: self.orders}

        target_position = signal * self.position_limit
        self.trade_to_target(target_position=target_position, fair_price=mean_price)
        return {self.name: self.orders}


class MarketMakingTrader(ProductTrader):
    def __init__(self, name, state, prints, new_trader_data):
        super().__init__(name, state, prints, new_trader_data)

    def get_orders(self):
        # Placeholder for future strategy modules.
        self.log("status", "placeholder")
        return {self.name: self.orders}


class Trader:
    def run(self, state: TradingState):
        result = {}
        conversions = 0
        new_trader_data = {}
        prints = {
            "GENERAL": {
                "timestamp": state.timestamp,
                "positions": state.position,
            }
        }

        for symbol, config in STRATEGY_CONFIG.items():
            if symbol not in state.order_depths:
                continue

            try:
                if config["type"] == "mean_reversion":
                    trader = MeanReversionTrader(
                        name=symbol,
                        state=state,
                        prints=prints,
                        new_trader_data=new_trader_data,
                        config=MEAN_REVERSION_CONFIG[symbol],
                    )
                elif config["type"] == "market_making_placeholder":
                    trader = MarketMakingTrader(
                        name=symbol,
                        state=state,
                        prints=prints,
                        new_trader_data=new_trader_data,
                    )
                else:
                    continue

                result.update(trader.get_orders())
            except Exception as exc:
                error_group = prints.get("ERRORS", {})
                error_group[symbol] = str(exc)
                prints["ERRORS"] = error_group

        try:
            trader_data = json.dumps(new_trader_data)
        except Exception:
            trader_data = ""

        try:
            print(json.dumps(prints))
        except Exception:
            pass

        return result, conversions, trader_data
