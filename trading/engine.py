"""Engine that drives the trading simulation."""

import pandas as pd
from typing import Optional
from .subject import MarketDataSubject
from .observers import VolatilityBreakoutStrategyObserver
from .broker import Broker


class Engine:
    """Engine that orchestrates market data flow and trading execution."""

    def __init__(
        self,
        subject: MarketDataSubject,
        strategy: VolatilityBreakoutStrategyObserver,
        broker: Broker,
        risk_observer: Optional[object] = None,
    ):
        """Initialize the engine.

        Args:
            subject: Market data subject for broadcasting prices.
            strategy: Strategy observer that generates trading signals.
            broker: Broker for executing orders.
            risk_observer: Optional risk observer for position monitoring.
        """
        self.subject = subject
        self.strategy = strategy
        self.broker = broker
        self.risk_observer = risk_observer

    def run(self, prices: pd.Series, order_size: int = 100) -> float:
        """Run the trading simulation over a price series.

        Args:
            prices: Series of market prices to process.
            order_size: Fixed quantity for each order.

        Returns:
            Final equity (cash + position * last_price).
        """
        if len(prices) == 0:
            return self.broker.cash

        last_price = float(prices.iloc[-1])

        for idx, price in enumerate(prices):
            price_float = float(price)

            # Skip invalid prices
            if not pd.notna(price_float) or price_float <= 0:
                continue

            # Notify all observers of the new price
            try:
                self.subject.notify(price_float)
            except Exception as e:
                # Log but continue - one observer failure shouldn't stop the engine
                # In production, you might want more sophisticated error handling
                print(f"Warning: Observer update failed: {e}")

            # Get signal from strategy (based on previous prices, so we use signal from t-1)
            # For the first price, signal will be 0 anyway
            signal = self.strategy.last_signal

            # Execute order based on signal
            if signal != 0 and idx > 0:  # Skip first price (no signal yet)
                try:
                    side = "buy" if signal > 0 else "sell"
                    self.broker.market_order(side, order_size, price_float)

                    # Check risk limits if risk observer is attached
                    if self.risk_observer is not None:
                        self.risk_observer.check_position(self.broker.position)

                except ValueError as e:
                    # Order failed (insufficient cash/shares) - log and continue
                    print(f"Warning: Order failed: {e}")

        return self.broker.get_equity(last_price)

