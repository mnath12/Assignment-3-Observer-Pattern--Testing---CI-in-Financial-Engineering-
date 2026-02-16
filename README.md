# Observer Pattern Trading System

A minimal market data broadcasting system implementing the Observer pattern for financial engineering applications.

## Overview

This project demonstrates the Observer design pattern in a trading system context, where market data updates are pushed to multiple observers (strategies, risk management, logging). The system includes comprehensive test coverage and CI/CD integration.

## Features

- **Observer Pattern Implementation**: Clean separation between data source (Subject) and consumers (Observers)
- **Multiple Observer Types**:
  - `VolatilityBreakoutStrategyObserver`: Generates trading signals based on volatility breakouts
  - `RiskObserver`: Monitors position limits and risk metrics
  - `LoggerObserver`: Records all price updates for analysis
- **Broker**: Executes market orders and tracks cash/position
- **Engine**: Orchestrates the trading simulation loop
- **Comprehensive Testing**: ≥90% code coverage with pytest
- **CI/CD**: Automated testing via GitHub Actions

## Project Structure

```
observer-ci-lab/
├── trading/
│   ├── __init__.py
│   ├── subject.py        # MarketDataSubject
│   ├── observers.py      # StrategyObserver, RiskObserver, LoggerObserver
│   ├── broker.py         # Broker for order execution
│   └── engine.py         # Trading engine
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   ├── test_subject.py
│   ├── test_observers.py
│   ├── test_broker.py
│   └── test_engine.py
├── .github/workflows/
│   └── ci.yml            # GitHub Actions CI pipeline
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd observer-ci-lab
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import pandas as pd
from trading import (
    MarketDataSubject,
    VolatilityBreakoutStrategyObserver,
    LoggerObserver,
    Broker,
    Engine,
)

# Create components
subject = MarketDataSubject()
strategy = VolatilityBreakoutStrategyObserver(window=20)
logger = LoggerObserver()
broker = Broker(cash=1_000_000)

# Attach observers
subject.attach(strategy)
subject.attach(logger)

# Create and run engine
engine = Engine(subject, strategy, broker)
prices = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0])
final_equity = engine.run(prices)

print(f"Final equity: ${final_equity:,.2f}")
print(f"Logged {len(logger.prices)} prices")
```

### Observer Pattern Usage

```python
from trading import MarketDataSubject, LoggerObserver

subject = MarketDataSubject()
observer1 = LoggerObserver()
observer2 = LoggerObserver()

# Attach observers
subject.attach(observer1)
subject.attach(observer2)

# Notify all observers
subject.notify(100.0)
subject.notify(101.0)

# Detach an observer
subject.detach(observer1)

# Only observer2 receives future updates
subject.notify(102.0)
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
coverage run -m pytest
coverage report
```

The test suite includes:
- Unit tests for all components
- Integration tests for observer-subject interactions
- Edge case handling (invalid prices, insufficient funds, etc.)
- Failure mode testing

## Design Decisions

### Observer Failure Handling

When an observer's `update()` method raises an exception:
- The `MarketDataSubject.notify()` method attempts to notify all observers, even if some fail
- If any observer raises an exception, all observers are still attempted, then the first exception is propagated
- The `Engine.run()` method catches exceptions from `notify()` and continues processing (with a warning)
- This design allows for graceful degradation: one failing observer doesn't stop other observers from receiving updates, and the engine continues processing subsequent prices

### Signal Timing

The `Engine` uses signals from the previous time step (t-1) when making trading decisions at time t. This ensures that:
- Signals are based on complete price information
- No look-ahead bias in trading decisions

### Risk Observer Integration

The `RiskObserver` is designed to be checked after position updates, not during price updates. This separation allows:
- Risk checks to be performed with full context (position + price)
- Flexible risk monitoring strategies

## CI/CD

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:
- Runs tests on every push and pull request
- Enforces ≥90% code coverage
- Tests on Python 3.11

## Requirements

- Python ≥3.8
- pytest ≥7.4.0
- coverage ≥7.3.0
- pandas ≥2.0.0
- numpy ≥1.24.0

## License

This project is for educational purposes.

