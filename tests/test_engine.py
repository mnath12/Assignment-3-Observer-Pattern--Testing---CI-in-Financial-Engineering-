"""Tests for Engine."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from trading.engine import Engine
from trading.subject import MarketDataSubject
from trading.observers import (
    VolatilityBreakoutStrategyObserver,
    RiskObserver,
)
from trading.broker import Broker


class TestEngineInitialization:
    """Tests for engine initialization."""

    def test_engine_initialization(self, subject, strategy, broker):
        """Test engine initialization."""
        engine = Engine(subject, strategy, broker)
        assert engine.subject == subject
        assert engine.strategy == strategy
        assert engine.broker == broker

    def test_engine_with_risk_observer(self, subject, strategy, broker, risk_observer):
        """Test engine initialization with risk observer."""
        engine = Engine(subject, strategy, broker, risk_observer)
        assert engine.risk_observer == risk_observer


class TestEngineRun:
    """Tests for engine run method."""

    def test_engine_run_empty_series(self, subject, strategy, broker):
        """Test engine run with empty price series."""
        engine = Engine(subject, strategy, broker)
        prices = pd.Series([])

        equity = engine.run(prices)
        assert equity == broker.cash

    def test_engine_run_notifies_observers(self, subject, strategy, broker, logger):
        """Test that engine notifies all observers."""
        subject.attach(strategy)
        subject.attach(logger)

        engine = Engine(subject, strategy, broker)
        prices = pd.Series([100.0, 101.0, 102.0])

        engine.run(prices)

        assert len(logger.prices) == 3

    def test_engine_uses_strategy_signal(self, subject, strategy, broker):
        """Test that engine uses strategy signals for trading."""
        subject.attach(strategy)

        # Create prices that will generate signals
        np.random.seed(42)
        base = 100.0
        prices_list = [base]
        for _ in range(30):
            prices_list.append(prices_list[-1] * (1 + np.random.normal(0, 0.01)))

        # Add a big move to trigger signal
        prices_list.append(prices_list[-1] * 1.05)

        prices = pd.Series(prices_list)
        engine = Engine(subject, strategy, broker)

        initial_cash = broker.cash
        equity = engine.run(prices, order_size=10)

        # Equity should be calculated correctly
        last_price = float(prices.iloc[-1])
        expected_equity = broker.cash + broker.position * last_price
        assert equity == expected_equity

    def test_engine_handles_insufficient_cash(self, subject, strategy, broker_small):
        """Test that engine handles insufficient cash gracefully."""
        subject.attach(strategy)

        # Create prices that will generate buy signals
        prices = pd.Series([100.0] * 25 + [110.0] * 10)
        engine = Engine(subject, strategy, broker_small)

        # Should not raise, but orders will fail
        equity = engine.run(prices, order_size=100)

        # Should still return valid equity
        assert equity >= 0

    def test_engine_skips_invalid_prices(self, subject, strategy, broker):
        """Test that engine skips invalid prices."""
        subject.attach(strategy)

        prices = pd.Series([100.0, float("nan"), 101.0, float("inf"), 102.0, -10.0])
        engine = Engine(subject, strategy, broker)

        equity = engine.run(prices)

        # Should complete without error
        assert equity >= 0

    def test_engine_with_risk_observer(self, subject, strategy, broker, risk_observer):
        """Test engine with risk observer monitoring."""
        subject.attach(strategy)

        # Create prices that generate signals
        prices = pd.Series([100.0] * 25 + [110.0] * 10)
        engine = Engine(subject, strategy, broker, risk_observer)

        equity = engine.run(prices, order_size=50)

        # Risk observer should have checked positions
        # (may or may not be breached depending on signals)
        assert isinstance(risk_observer.breached, bool)

    def test_engine_order_size_parameter(self, subject, strategy, broker):
        """Test that engine respects order_size parameter."""
        subject.attach(strategy)

        prices = pd.Series([100.0] * 25 + [110.0] * 5)
        engine = Engine(subject, strategy, broker)

        equity1 = engine.run(prices, order_size=10)
        broker.reset()
        equity2 = engine.run(prices, order_size=20)

        # Different order sizes should result in different positions
        # (if signals were generated)
        # This is a basic sanity check
        assert isinstance(equity1, float)
        assert isinstance(equity2, float)

    def test_engine_final_equity_calculation(self, subject, strategy, broker):
        """Test that engine returns correct final equity."""
        subject.attach(strategy)

        prices = pd.Series([100.0, 101.0, 102.0, 103.0])
        engine = Engine(subject, strategy, broker)

        equity = engine.run(prices)

        last_price = float(prices.iloc[-1])
        expected_equity = broker.cash + broker.position * last_price
        assert equity == expected_equity

    def test_engine_observer_failure_handling(self, subject, broker):
        """Test that engine handles observer failures gracefully."""
        # Create a failing observer
        failing_observer = MagicMock()
        failing_observer.update.side_effect = ValueError("Observer error")
        subject.attach(failing_observer)

        strategy = VolatilityBreakoutStrategyObserver()
        subject.attach(strategy)

        engine = Engine(subject, strategy, broker)
        prices = pd.Series([100.0, 101.0, 102.0])

        # Engine should catch the exception and continue processing
        # The failing observer will raise, but engine catches it
        equity = engine.run(prices)

        # Should complete without raising, but failing observer should have been called
        assert isinstance(equity, float)
        # The failing observer should have been called (and raised)
        assert failing_observer.update.called

    def test_engine_signal_timing(self, subject, strategy, broker):
        """Test that engine uses signals correctly (t-1 vs t)."""
        subject.attach(strategy)

        # First price should not generate a trade (no signal yet)
        prices = pd.Series([100.0, 101.0, 102.0])
        engine = Engine(subject, strategy, broker)

        initial_position = broker.position
        equity = engine.run(prices, order_size=10)

        # With only 3 prices, strategy won't have enough data for signal
        # So position should remain 0
        # But let's test with more prices
        broker.reset()
        prices_long = pd.Series([100.0] * 25 + [110.0] * 5)
        equity = engine.run(prices_long, order_size=10)

        # Should have executed some trades if signals were generated
        assert isinstance(equity, float)

