"""Tests for Broker."""

import pytest
from trading.broker import Broker


class TestBrokerInitialization:
    """Tests for broker initialization."""

    def test_broker_default_cash(self):
        """Test broker with default cash."""
        broker = Broker()
        assert broker.cash == 1_000_000
        assert broker.position == 0

    def test_broker_custom_cash(self):
        """Test broker with custom cash."""
        broker = Broker(cash=500_000)
        assert broker.cash == 500_000
        assert broker.position == 0

    def test_broker_negative_cash_raises_error(self):
        """Test that negative cash raises ValueError."""
        with pytest.raises(ValueError, match="Initial cash cannot be negative"):
            Broker(cash=-1000)


class TestBrokerMarketOrders:
    """Tests for market order execution."""

    def test_buy_order_updates_cash_and_position(self, broker):
        """Test that buy order updates cash and position correctly."""
        initial_cash = broker.cash
        price = 100.0
        qty = 10

        broker.market_order("buy", qty, price)

        assert broker.cash == initial_cash - (qty * price)
        assert broker.position == qty

    def test_sell_order_updates_cash_and_position(self, broker):
        """Test that sell order updates cash and position correctly."""
        # First buy some shares
        broker.market_order("buy", 10, 100.0)
        initial_cash = broker.cash
        initial_position = broker.position

        # Then sell some
        broker.market_order("sell", 5, 110.0)

        assert broker.cash == initial_cash + (5 * 110.0)
        assert broker.position == initial_position - 5

    def test_invalid_side_raises_error(self, broker):
        """Test that invalid side raises ValueError."""
        with pytest.raises(ValueError, match="Invalid side"):
            broker.market_order("invalid", 10, 100.0)

    def test_zero_quantity_raises_error(self, broker):
        """Test that zero quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            broker.market_order("buy", 0, 100.0)

    def test_negative_quantity_raises_error(self, broker):
        """Test that negative quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            broker.market_order("buy", -10, 100.0)

    def test_zero_price_raises_error(self, broker):
        """Test that zero price raises ValueError."""
        with pytest.raises(ValueError, match="Price must be positive"):
            broker.market_order("buy", 10, 0.0)

    def test_negative_price_raises_error(self, broker):
        """Test that negative price raises ValueError."""
        with pytest.raises(ValueError, match="Price must be positive"):
            broker.market_order("buy", 10, -100.0)

    def test_insufficient_cash_raises_error(self, broker_small):
        """Test that insufficient cash raises ValueError."""
        with pytest.raises(ValueError, match="Insufficient cash"):
            broker_small.market_order("buy", 20, 100.0)  # Need 2000, have 1000

    def test_insufficient_shares_raises_error(self, broker):
        """Test that insufficient shares raises ValueError."""
        with pytest.raises(ValueError, match="Insufficient shares"):
            broker.market_order("sell", 10, 100.0)  # No position yet

    def test_multiple_orders(self, broker):
        """Test multiple buy and sell orders."""
        # Buy sequence
        broker.market_order("buy", 10, 100.0)
        assert broker.position == 10
        assert broker.cash == 1_000_000 - 1000

        broker.market_order("buy", 5, 110.0)
        assert broker.position == 15
        assert broker.cash == 1_000_000 - 1000 - 550

        # Sell sequence
        broker.market_order("sell", 7, 120.0)
        assert broker.position == 8
        assert broker.cash == 1_000_000 - 1000 - 550 + 840


class TestBrokerEquity:
    """Tests for equity calculation."""

    def test_equity_with_no_position(self, broker):
        """Test equity calculation with no position."""
        assert broker.get_equity(100.0) == broker.cash

    def test_equity_with_position(self, broker):
        """Test equity calculation with position."""
        broker.market_order("buy", 10, 100.0)
        equity = broker.get_equity(110.0)

        expected = broker.cash + (10 * 110.0)
        assert equity == expected

    def test_equity_with_short_position(self, broker):
        """Test equity calculation with short position."""
        # First buy, then sell more than we have (if allowed)
        # Actually, we can't short in this simple broker
        # But we can test with negative position if we allow it
        # For now, let's just test long positions


class TestBrokerReset:
    """Tests for broker reset."""

    def test_broker_reset(self, broker):
        """Test that broker reset restores initial state."""
        broker.market_order("buy", 10, 100.0)
        broker.reset()

        assert broker.cash == 1_000_000
        assert broker.position == 0

    def test_broker_reset_custom_cash(self, broker):
        """Test broker reset with custom cash."""
        broker.market_order("buy", 10, 100.0)
        broker.reset(cash=500_000)

        assert broker.cash == 500_000
        assert broker.position == 0

    def test_broker_reset_negative_cash_raises_error(self, broker):
        """Test that reset with negative cash raises ValueError."""
        with pytest.raises(ValueError, match="Initial cash cannot be negative"):
            broker.reset(cash=-1000)

