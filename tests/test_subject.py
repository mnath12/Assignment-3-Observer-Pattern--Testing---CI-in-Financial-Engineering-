"""Tests for MarketDataSubject."""

import pytest
from unittest.mock import MagicMock, call
from trading.subject import MarketDataSubject


def test_attach_and_notify_calls_update():
    """Test that attaching an observer and notifying calls update."""
    subject = MarketDataSubject()
    obs = MagicMock()
    subject.attach(obs)

    subject.notify(101.0)

    obs.update.assert_called_once_with(101.0)


def test_attach_multiple_observers():
    """Test that multiple observers receive notifications."""
    subject = MarketDataSubject()
    obs1 = MagicMock()
    obs2 = MagicMock()
    obs3 = MagicMock()

    subject.attach(obs1)
    subject.attach(obs2)
    subject.attach(obs3)

    subject.notify(105.0)

    obs1.update.assert_called_once_with(105.0)
    obs2.update.assert_called_once_with(105.0)
    obs3.update.assert_called_once_with(105.0)


def test_detach_stops_notifications():
    """Test that detaching an observer stops notifications."""
    subject = MarketDataSubject()
    obs = MagicMock()
    subject.attach(obs)
    subject.detach(obs)

    subject.notify(101.0)

    obs.update.assert_not_called()


def test_detach_one_observer_keeps_others():
    """Test that detaching one observer doesn't affect others."""
    subject = MarketDataSubject()
    obs1 = MagicMock()
    obs2 = MagicMock()

    subject.attach(obs1)
    subject.attach(obs2)
    subject.detach(obs1)

    subject.notify(102.0)

    obs1.update.assert_not_called()
    obs2.update.assert_called_once_with(102.0)


def test_detach_nonexistent_observer_no_error():
    """Test that detaching a non-attached observer doesn't raise an error."""
    subject = MarketDataSubject()
    obs = MagicMock()

    # Should not raise
    subject.detach(obs)


def test_attach_duplicate_observer_ignored():
    """Test that attaching the same observer twice doesn't duplicate."""
    subject = MarketDataSubject()
    obs = MagicMock()

    subject.attach(obs)
    subject.attach(obs)

    subject.notify(103.0)

    # Should only be called once, not twice
    assert obs.update.call_count == 1


def test_notify_order_preserved():
    """Test that observers are notified in attachment order."""
    subject = MarketDataSubject()
    obs1 = MagicMock()
    obs2 = MagicMock()
    obs3 = MagicMock()

    subject.attach(obs1)
    subject.attach(obs2)
    subject.attach(obs3)

    subject.notify(104.0)

    # Verify call order
    expected_calls = [call(104.0), call(104.0), call(104.0)]
    assert obs1.update.call_args_list == [expected_calls[0]]
    assert obs2.update.call_args_list == [expected_calls[1]]
    assert obs3.update.call_args_list == [expected_calls[2]]


def test_attach_none_raises_error():
    """Test that attaching None raises ValueError."""
    subject = MarketDataSubject()

    with pytest.raises(ValueError, match="Observer cannot be None"):
        subject.attach(None)


def test_observer_count():
    """Test the observer_count property."""
    subject = MarketDataSubject()
    assert subject.observer_count == 0

    obs1 = MagicMock()
    obs2 = MagicMock()

    subject.attach(obs1)
    assert subject.observer_count == 1

    subject.attach(obs2)
    assert subject.observer_count == 2

    subject.detach(obs1)
    assert subject.observer_count == 1


def test_notify_with_failing_observer():
    """Test that one failing observer doesn't stop others from being notified."""
    subject = MarketDataSubject()
    obs1 = MagicMock()
    obs1.update.side_effect = ValueError("Test error")
    obs2 = MagicMock()

    subject.attach(obs1)
    subject.attach(obs2)

    # Should raise the error
    with pytest.raises(ValueError, match="Test error"):
        subject.notify(106.0)

    # But obs2 should still have been called
    obs2.update.assert_called_once_with(106.0)

