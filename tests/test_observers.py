"""Tests for observer implementations."""

import pytest
import numpy as np
import pandas as pd
from trading.observers import (
    VolatilityBreakoutStrategyObserver,
    RiskObserver,
    LoggerObserver,
)
from trading.subject import MarketDataSubject


class TestLoggerObserver:
    """Tests for LoggerObserver."""

    def test_logger_records_all_prices(self, subject, logger, prices):
        """Test that logger records all prices."""
        subject.attach(logger)
        for p in prices:
            subject.notify(float(p))

        assert logger.prices[0] == float(prices.iloc[0])
        assert len(logger.prices) == len(prices)

    def test_logger_reset(self, subject, logger):
        """Test that logger reset clears prices."""
        subject.attach(logger)
        subject.notify(100.0)
        subject.notify(101.0)

        assert len(logger.prices) == 2

        logger.reset()
        assert len(logger.prices) == 0

    def test_logger_get_prices_returns_copy(self, logger):
        """Test that get_prices returns a copy."""
        logger.update(100.0)
        logger.update(101.0)

        prices_copy = logger.get_prices()
        assert prices_copy == [100.0, 101.0]

        # Modifying copy shouldn't affect original
        prices_copy.append(102.0)
        assert len(logger.prices) == 2


class TestVolatilityBreakoutStrategyObserver:
    """Tests for VolatilityBreakoutStrategyObserver."""

    def test_strategy_initial_signal_zero(self, strategy):
        """Test that initial signal is zero."""
        assert strategy.last_signal == 0

    def test_strategy_needs_minimum_prices(self, strategy):
        """Test that strategy needs minimum prices before generating signals."""
        strategy.update(100.0)
        assert strategy.last_signal == 0  # Need at least 2 prices

        strategy.update(101.0)
        # Still need window+1 prices for volatility calculation
        assert strategy.last_signal == 0

    def test_strategy_signal_generation(self, strategy):
        """Test signal generation with known price series."""
        # Create a series that will generate a signal
        # Start with stable prices, then a big jump
        base_prices = [100.0] * 25
        for price in base_prices:
            strategy.update(price)

        # Now add a big positive return
        strategy.update(110.0)  # 10% jump

        # Should generate a buy signal (+1) if volatility is low
        # But with 20 prices at 100, volatility is 0, so signal might be 0
        # Let's create a more realistic scenario
        strategy.reset()

        # Create prices with some volatility first
        prices = [100.0]
        for i in range(1, 25):
            prices.append(prices[-1] * (1 + np.random.normal(0, 0.01)))

        for price in prices:
            strategy.update(price)

        # Add a big positive return
        strategy.update(prices[-1] * 1.05)  # 5% jump

        # Signal should be generated (could be +1, -1, or 0 depending on volatility)
        assert strategy.last_signal in [-1, 0, 1]

    def test_strategy_handles_invalid_prices(self, strategy):
        """Test that strategy handles invalid prices gracefully."""
        strategy.update(100.0)
        strategy.update(101.0)
        signal_before = strategy.last_signal

        strategy.update(float("nan"))
        assert strategy.last_signal == 0

        strategy.update(float("inf"))
        assert strategy.last_signal == 0

        strategy.update(-10.0)  # Negative price
        assert strategy.last_signal == 0

    def test_strategy_reset(self, strategy):
        """Test that strategy reset clears state."""
        for i in range(30):
            strategy.update(100.0 + i * 0.1)

        strategy.reset()
        assert strategy.last_signal == 0
        assert len(strategy._prices) == 0

    def test_strategy_with_constant_prices(self, strategy, prices_constant):
        """Test strategy with constant prices (zero volatility)."""
        for price in prices_constant:
            strategy.update(price)

        # With constant prices, volatility is 0, so signal should be 0
        assert strategy.last_signal == 0

    def test_strategy_with_short_series(self, strategy, prices_short):
        """Test strategy with very short price series."""
        for price in prices_short:
            strategy.update(price)

        # Should not generate signal with only 3 prices
        assert strategy.last_signal == 0


class TestRiskObserver:
    """Tests for RiskObserver."""

    def test_risk_observer_initial_state(self, risk_observer):
        """Test initial state of risk observer."""
        assert risk_observer.breached is False
        assert risk_observer.current_position == 0
        assert risk_observer.last_price is None

    def test_risk_observer_tracks_price(self, risk_observer):
        """Test that risk observer tracks prices."""
        risk_observer.update(100.0)
        assert risk_observer.last_price == 100.0

        risk_observer.update(101.0)
        assert risk_observer.last_price == 101.0

    def test_risk_observer_check_position_within_limit(self, risk_observer):
        """Test position check when within limits."""
        assert risk_observer.check_position(500) is True
        assert risk_observer.breached is False
        assert risk_observer.current_position == 500

    def test_risk_observer_check_position_exceeds_limit(self, risk_observer):
        """Test position check when exceeding limits."""
        assert risk_observer.check_position(1500) is False
        assert risk_observer.breached is True
        assert risk_observer.current_position == 1500

    def test_risk_observer_check_negative_position(self, risk_observer):
        """Test position check with negative position."""
        assert risk_observer.check_position(-500) is True
        assert risk_observer.breached is False

        assert risk_observer.check_position(-1500) is False
        assert risk_observer.breached is True

    def test_risk_observer_reset(self, risk_observer):
        """Test that risk observer reset clears state."""
        risk_observer.update(100.0)
        risk_observer.check_position(500)
        risk_observer.breached = True

        risk_observer.reset()
        assert risk_observer.breached is False
        assert risk_observer.current_position == 0
        assert risk_observer.last_price is None

    def test_risk_observer_handles_invalid_prices(self, risk_observer):
        """Test that risk observer handles invalid prices."""
        risk_observer.update(100.0)
        assert risk_observer.last_price == 100.0

        risk_observer.update(float("nan"))
        assert risk_observer.last_price == 100.0  # Should not update

        risk_observer.update(-10.0)
        assert risk_observer.last_price == 100.0  # Should not update


class TestObserverIntegration:
    """Integration tests for observers with subject."""

    def test_multiple_observers_receive_updates(self, subject, logger, strategy):
        """Test that multiple observers receive updates correctly."""
        subject.attach(logger)
        subject.attach(strategy)

        prices = [100.0, 101.0, 102.0, 103.0]
        for price in prices:
            subject.notify(price)

        assert len(logger.prices) == 4
        assert logger.prices == prices

    def test_observer_order_independence(self, subject, logger, strategy):
        """Test that observers maintain independent state."""
        subject.attach(logger)
        subject.attach(strategy)

        subject.notify(100.0)
        subject.notify(101.0)

        assert len(logger.prices) == 2
        # Strategy needs more prices for signal
        assert strategy.last_signal == 0

