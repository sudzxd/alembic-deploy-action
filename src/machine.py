"""Generic State Machine implementation with observer support."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

# Project/Local
from src.logger import setup_logger

if TYPE_CHECKING:
    from src.observers import StateObserver

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
logger = setup_logger(__name__)

T = TypeVar("T")


# =============================================================================
# CORE CLASSES
# =============================================================================
class State(ABC, Generic[T]):
    """Abstract base state."""

    @abstractmethod
    def handle(self, context: T) -> State[T] | None:
        """Handle execution for this state.

        Args:
            context: The shared context object.

        Returns:
            The next State to transition to, or None if terminal.
        """
        pass


class StateMachine(Generic[T]):
    """Generic State Machine with observer support."""

    def __init__(self, initial_state: State[T], context: T):
        """Initialize state machine.

        Args:
            initial_state: Starting state.
            context: Shared context.
        """
        self.current_state: State[T] | None = initial_state
        self.context = context
        self._observers: list[StateObserver[T]] = []

    def add_observer(self, observer: StateObserver[T]) -> None:
        """Add an observer to receive state change notifications.

        Args:
            observer: Observer to add.
        """
        self._observers.append(observer)

    def remove_observer(self, observer: StateObserver[T]) -> None:
        """Remove an observer.

        Args:
            observer: Observer to remove.
        """
        self._observers.remove(observer)

    def run(self) -> None:
        """Run the state machine until completion."""
        while self.current_state:
            state_name = self.current_state.__class__.__name__

            # Notify observers of state entry
            self._notify_enter(state_name)

            try:
                next_state = self.current_state.handle(self.context)

                # Notify observers of state exit
                self._notify_exit(state_name)

                self.current_state = next_state
            except Exception as e:
                # Notify observers of error
                self._notify_error(state_name, e)
                raise

    def _notify_enter(self, state_name: str) -> None:
        """Notify observers of state entry."""
        for observer in self._observers:
            observer.on_state_enter(state_name, self.context)

    def _notify_exit(self, state_name: str) -> None:
        """Notify observers of state exit."""
        for observer in self._observers:
            observer.on_state_exit(state_name, self.context)

    def _notify_error(self, state_name: str, error: Exception) -> None:
        """Notify observers of error."""
        for observer in self._observers:
            observer.on_error(state_name, error, self.context)
