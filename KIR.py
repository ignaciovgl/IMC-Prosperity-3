from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import statistics

class Trader:

    def __init__(self):
        self.traderData = {
            "squid_ink_prices": []
        }
        self.position_limits = {
            "RAINFOREST_RESIN": 50,
            "KELP": 50,
            "SQUID_INK": 50,
        }
        self.currency = "SEASHELLS"
        self.available_capital = 100000000

        # Linear regression coefficients for KELP (replace with yours)
        self.kelp_coef = 9.05174264e-06
        self.kelp_intercept = 2009.3154445130767

        # Historical price tracking for failsafe
        self.kelp_history = []
        self.failsafe_threshold = 5  # e.g., significant drop in mid-price

    def get_mid_price(self, state, product) -> float:
        order_depth = state.order_depths.get(product, None)
        if order_depth and order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders)
            best_bid = max(order_depth.buy_orders)
            return (best_ask + best_bid) / 2
        return 0

    def calc_next_price_kelp(self, time: int) -> float:
        return int(self.kelp_coef * (time + 4000000) + self.kelp_intercept)

    def run(self, state: TradingState):
        result = {}
        timestamp = state.timestamp


        for product in ["RAINFOREST_RESIN", "KELP","SQUID_INK"]:
            if product not in state.order_depths:
                continue

            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            current_position = state.position.get(product, 0)
            max_buy_quantity = self.position_limits[product] - current_position
            max_sell_quantity = self.position_limits[product] + current_position

            # === SQUID_INK Strategy ===
            if product == "SQUID_INK":
                mid_price = self.get_mid_price(state, product)
                if mid_price == 0:
                    return {}, 0, ""
        
                # Track mid price
                self.traderData["squid_ink_prices"].append(mid_price)
                if len(self.traderData["squid_ink_prices"]) > 10:
                    self.traderData["squid_ink_prices"].pop(0)
        
                # Only act if we have enough data
                if len(self.traderData["squid_ink_prices"]) == 10:
                    mean_price = statistics.mean(self.traderData["squid_ink_prices"])
                    std_dev = statistics.stdev(self.traderData["squid_ink_prices"])
        
                    if std_dev > 0:
                        z_score = (mid_price - mean_price) / std_dev
        
                        # Sudden drop (mean-reversion play)
                        if z_score < -2.5 and len(order_depth.sell_orders) > 0:
                            best_ask = min(order_depth.sell_orders)
                            ask_volume = order_depth.sell_orders[best_ask]
                            buy_quantity = min(-ask_volume, max_buy_quantity)
                            if buy_quantity > 0:
                                orders.append(Order(product, best_ask, buy_quantity))
        
                        # Sudden spike (mean-reversion sell)
                        elif z_score > 2.5 and len(order_depth.buy_orders) > 0:
                            best_bid = max(order_depth.buy_orders)
                            bid_volume = order_depth.buy_orders[best_bid]
                            sell_quantity = min(bid_volume, max_sell_quantity)
                            if sell_quantity > 0:
                                orders.append(Order(product, best_bid, -sell_quantity))

            if product == "KELP":
                predicted_price = self.calc_next_price_kelp(timestamp)
                mid_price = self.get_mid_price(state, product)

                # === FAILSAFE logic ===
                self.kelp_history.append(mid_price)
                if len(self.kelp_history) > 5:
                    recent_change = self.kelp_history[-1] - self.kelp_history[-5]
                    if recent_change < -self.failsafe_threshold:
                        print(f"[Time {timestamp}] Failsafe activated for KELP, recent change: {recent_change:.2f}")
                        result[product] = orders  # Skip trading if sharp drop
                        continue

                buy_threshold = predicted_price - 0.5
                sell_threshold = predicted_price + 0.5

            else:  # Resin logic (unchanged)
                buy_threshold = 9999
                sell_threshold = 10001

            # === BUY Logic ===
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if best_ask < buy_threshold:
                    buy_quantity = min(-best_ask_amount, max_buy_quantity, self.available_capital // int(best_ask))
                    if buy_quantity > 0:
                        orders.append(Order(product, best_ask, buy_quantity))
                        self.available_capital -= buy_quantity * int(best_ask)

            # === SELL Logic ===
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if best_bid > sell_threshold:
                    sell_quantity = min(best_bid_amount, max_sell_quantity, self.available_capital // int(best_bid))
                    if sell_quantity > 0:
                        orders.append(Order(product, best_bid, -sell_quantity))
                        self.available_capital += sell_quantity * int(best_bid)

            result[product] = orders

        return result, 0, ""
