"""Observer implementations for market data updates."""

import numpy as np
from typing import Optional


class VolatilityBreakoutStrategyObserver:
    """Strategy observer that generates signals based on volatility breakout.

    Maintains a rolling window of returns and emits signals when the latest
    return exceeds the rolling volatility threshold.
    """

    def __init__(self, window: int = 20):
        """Initialize the strategy observer.

        Args:
            window: Size of the rolling window for volatility calculation.
        """
        self.window = window
        self._prices: list[float] = []
        self._last_signal: int = 0

    def update(self, price: float) -> None:
        """Update with a new price and compute signal.

        Args:
            price: The new market price.
        """
        if not np.isfinite(price) or price <= 0:
            self._last_signal = 0
            return

        self._prices.append(price)

        # Need at least 2 prices to compute returns
        if len(self._prices) < 2:
            self._last_signal = 0
            return

        # Compute returns
        returns = []
        for i in range(1, len(self._prices)):
            ret = (self._prices[i] - self._prices[i - 1]) / self._prices[i - 1]
            returns.append(ret)

        # Need at least window returns to compute rolling volatility
        if len(returns) < self.window:
            self._last_signal = 0
            return

        # Get the latest return and rolling window
        latest_return = returns[-1]
        rolling_returns = returns[-self.window:]

        # Compute rolling volatility (std of returns)
        rolling_vol = np.std(rolling_returns)

        # Generate signal: +1 if return > vol, -1 if return < -vol, else 0
        if rolling_vol > 0:
            if latest_return > rolling_vol:
                self._last_signal = 1
            elif latest_return < -rolling_vol:
                self._last_signal = -1
            else:
                self._last_signal = 0
        else:
            self._last_signal = 0

    @property
    def last_signal(self) -> int:
        """Get the last generated signal (-1, 0, or +1)."""
        return self._last_signal

    def reset(self) -> None:
        """Reset the price history and signal."""
        self._prices.clear()
        self._last_signal = 0


class RiskObserver:
    """Risk observer that monitors position limits."""

    def __init__(self, max_position: int):
        """Initialize the risk observer.

        Args:
            max_position: Maximum allowed position size (absolute value).
        """
        self.max_position = max_position
        self.breached = False
        self._current_position: int = 0
        self._last_price: Optional[float] = None

    def update(self, price: float) -> None:
        """Update with a new price and check risk limits.

        Args:
            price: The new market price.
        """
        if not np.isfinite(price) or price <= 0:
            return

        self._last_price = price
        # Risk check is done when position is updated externally
        # This observer just tracks prices for context

    def check_position(self, position: int) -> bool:
        """Check if the given position exceeds limits.

        Args:
            position: The current position to check.

        Returns:
            True if position is within limits, False if breached.
        """
        self._current_position = position
        if abs(position) > self.max_position:
            self.breached = True
            return False
        self.breached = False
        return True

    def reset(self) -> None:
        """Reset the risk observer state."""
        self.breached = False
        self._current_position = 0
        self._last_price = None

    @property
    def current_position(self) -> int:
        """Get the current tracked position."""
        return self._current_position

    @property
    def last_price(self) -> Optional[float]:
        """Get the last received price."""
        return self._last_price


class LoggerObserver:
    """Logger observer that records all price updates."""

    def __init__(self):
        """Initialize an empty price log."""
        self.prices: list[float] = []

    def update(self, price: float) -> None:
        """Record a price update.

        Args:
            price: The new market price to log.
        """
        self.prices.append(price)

    def reset(self) -> None:
        """Clear the price log."""
        self.prices.clear()

    def get_prices(self) -> list[float]:
        """Get a copy of all logged prices."""
        return self.prices.copy()

