"""Broker for executing market orders."""


class Broker:
    """Broker that executes market orders and tracks cash and position."""

    def __init__(self, cash: float = 1_000_000):
        """Initialize the broker with starting cash.

        Args:
            cash: Initial cash balance.
        """
        if cash < 0:
            raise ValueError("Initial cash cannot be negative")
        self.cash = cash
        self.position = 0

    def market_order(self, side: str, qty: int, price: float) -> None:
        """Execute a market order.

        Args:
            side: Order side, must be 'buy' or 'sell'.
            qty: Quantity to trade (must be positive).
            price: Execution price (must be positive).

        Raises:
            ValueError: If side is invalid, qty is non-positive, price is non-positive,
                       or insufficient cash/shares.
        """
        if side not in ("buy", "sell"):
            raise ValueError(f"Invalid side: {side}. Must be 'buy' or 'sell'")

        if qty <= 0:
            raise ValueError(f"Quantity must be positive, got {qty}")

        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}")

        cost = qty * price

        if side == "buy":
            if self.cash < cost:
                raise ValueError(
                    f"Insufficient cash: need {cost:.2f}, have {self.cash:.2f}"
                )
            self.cash -= cost
            self.position += qty
        else:  # sell
            if self.position < qty:
                raise ValueError(
                    f"Insufficient shares: need {qty}, have {self.position}"
                )
            self.cash += cost
            self.position -= qty

    def get_equity(self, current_price: float) -> float:
        """Calculate total equity (cash + position value).

        Args:
            current_price: Current market price for position valuation.

        Returns:
            Total equity value.
        """
        return self.cash + self.position * current_price

    def reset(self, cash: float = 1_000_000) -> None:
        """Reset broker to initial state.

        Args:
            cash: New initial cash balance.
        """
        if cash < 0:
            raise ValueError("Initial cash cannot be negative")
        self.cash = cash
        self.position = 0

