from datamodel import OrderDepth, TradingState, Order, ConversionObservation
from typing import List, Dict
import statistics

class Trader:
    def __init__(self):
        self.position_limits = {
            "MAGNIFICENT_MACARONS": 75
        }
        self.storage_cost = 0.1  # seashells per unit per timestamp

        # Tariff and transport fee values (adjust as needed)
        self.import_tariff = 5
        self.export_tariff = 5
        self.transport_fee = 2

        # Historical prices for Z-score strategy
        self.macaron_prices = []

    def get_mid_price(self, order_depth: OrderDepth) -> float:
        if order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders)
            best_bid = max(order_depth.buy_orders)
            return (best_ask + best_bid) / 2
        return 0

    def run(self, state: TradingState):
        result = {}
        conversions = []
        product = "MAGNIFICENT_MACARONS"

        if product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position = state.position.get(product, 0)
            max_pos = self.position_limits[product]

            # === Z-SCORE MEAN REVERSION STRATEGY ===
            mid_price = self.get_mid_price(order_depth)
            if mid_price > 0:
                self.macaron_prices.append(mid_price)
                if len(self.macaron_prices) > 10:
                    self.macaron_prices.pop(0)

                if len(self.macaron_prices) == 10:
                    mean_price = statistics.mean(self.macaron_prices)
                    std_dev = statistics.stdev(self.macaron_prices)

                    if std_dev > 0:
                        z_score = (mid_price - mean_price) / std_dev

                        # Mean reversion buy
                        if z_score < -2.5:
                            best_ask = min(order_depth.sell_orders)
                            ask_volume = order_depth.sell_orders[best_ask]
                            buy_qty = min(-ask_volume, max_pos - position)
                            if buy_qty > 0:
                                orders.append(Order(product, best_ask, buy_qty))

                        # Mean reversion sell
                        elif z_score > 2.5:
                            best_bid = max(order_depth.buy_orders)
                            bid_volume = order_depth.buy_orders[best_bid]
                            sell_qty = min(bid_volume, max_pos + position)
                            if sell_qty > 0:
                                orders.append(Order(product, best_bid, -sell_qty))

            # === CONVERSION ARBITRAGE STRATEGY ===
            if product in state.observations.conversion_observations:
                conv_obs: ConversionObservation = state.observations.conversion_observations[product]
                ask_price = conv_obs.askPrice
                bid_price = conv_obs.bidPrice

                # Full cost/revenue via conversion
                total_import_cost = ask_price + self.import_tariff + self.transport_fee
                total_export_revenue = bid_price - self.export_tariff - self.transport_fee

                # Buy from chefs, sell on market
                if len(order_depth.buy_orders) > 0:
                    best_market_bid = max(order_depth.buy_orders)
                    if total_import_cost < best_market_bid and position < max_pos:
                        conversions.append((product, min(10, max_pos - position), "BUY"))

                # Buy on market, sell to chefs
                if len(order_depth.sell_orders) > 0:
                    best_market_ask = min(order_depth.sell_orders)
                    if best_market_ask < total_export_revenue and position > -max_pos:
                        conversions.append((product, min(10, max_pos + position), "SELL"))

            result[product] = orders

        # Debugging / parameter logging
        trader_data = f"Tariffs: import={self.import_tariff}, export={self.export_tariff}, transport={self.transport_fee}"
        return result, conversions, trader_data