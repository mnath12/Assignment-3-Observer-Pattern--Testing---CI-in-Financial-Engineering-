"""Pytest configuration and shared fixtures."""

import numpy as np
import pandas as pd
import pytest

from trading.subject import MarketDataSubject
from trading.observers import (
    VolatilityBreakoutStrategyObserver,
    LoggerObserver,
    RiskObserver,
)
from trading.broker import Broker


@pytest.fixture
def prices():
    """Generate a synthetic price series."""
    return pd.Series(np.linspace(100, 120, 200))


@pytest.fixture
def prices_volatile():
    """Generate a volatile price series for strategy testing."""
    np.random.seed(42)
    base = 100
    returns = np.random.normal(0, 0.02, 100)
    prices = [base]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    return pd.Series(prices)


@pytest.fixture
def prices_constant():
    """Generate a constant price series."""
    return pd.Series([100.0] * 50)


@pytest.fixture
def prices_short():
    """Generate a short price series."""
    return pd.Series([100.0, 101.0, 102.0])


@pytest.fixture
def subject():
    """Create a MarketDataSubject instance."""
    return MarketDataSubject()


@pytest.fixture
def strategy():
    """Create a VolatilityBreakoutStrategyObserver instance."""
    return VolatilityBreakoutStrategyObserver(window=20)


@pytest.fixture
def logger():
    """Create a LoggerObserver instance."""
    return LoggerObserver()


@pytest.fixture
def risk_observer():
    """Create a RiskObserver instance."""
    return RiskObserver(max_position=1000)


@pytest.fixture
def broker():
    """Create a Broker instance with default cash."""
    return Broker(cash=1_000_000)


@pytest.fixture
def broker_small():
    """Create a Broker instance with small cash for testing limits."""
    return Broker(cash=1_000)

