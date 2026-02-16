"""Market data subject implementing the Observer pattern."""

from typing import Protocol, List


class Observer(Protocol):
    """Protocol defining the observer interface."""

    def update(self, price: float) -> None:
        """Called when a new price update is available.

        Args:
            price: The new market price.
        """
        ...


class MarketDataSubject:
    """Subject that maintains observers and notifies them of price updates."""

    def __init__(self):
        """Initialize an empty list of observers."""
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Attach an observer to receive price updates.

        Args:
            observer: The observer to attach.

        Raises:
            ValueError: If observer is None.
        """
        if observer is None:
            raise ValueError("Observer cannot be None")
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Detach an observer from receiving price updates.

        Args:
            observer: The observer to detach.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, price: float) -> None:
        """Notify all attached observers of a new price.

        Attempts to notify all observers even if some fail. If any observer
        raises an exception, it is propagated after all observers have been
        attempted.

        Args:
            price: The new market price to broadcast.

        Raises:
            Exception: The first exception raised by any observer, if any.
        """
        errors = []
        for observer in self._observers:
            try:
                observer.update(price)
            except Exception as e:
                errors.append(e)
        
        # If any observer failed, raise the first error
        if errors:
            raise errors[0]

    @property
    def observer_count(self) -> int:
        """Return the number of attached observers."""
        return len(self._observers)

