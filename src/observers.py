"""Observer protocol and implementations for state machine."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

# Project/Local
from src.constants import OUTPUT_MIGRATION_STATUS, STATUS_FAILED
from src.logger import setup_logger

if TYPE_CHECKING:
    from src.states import ActionContext

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
logger = setup_logger(__name__)

T_contra = TypeVar("T_contra", contravariant=True)


# =============================================================================
# PROTOCOLS
# =============================================================================
class StateObserver(Protocol[T_contra]):
    """Observer protocol for state machine events."""

    def on_state_enter(self, state_name: str, context: T_contra) -> None:
        """Called when entering a state."""
        ...

    def on_state_exit(self, state_name: str, context: T_contra) -> None:
        """Called when exiting a state."""
        ...

    def on_error(self, state_name: str, error: Exception, context: T_contra) -> None:
        """Called when an error occurs in a state."""
        ...


# =============================================================================
# IMPLEMENTATIONS
# =============================================================================
T = TypeVar("T")


class LoggingObserver(Generic[T]):
    """Logs state transitions for debugging."""

    def on_state_enter(self, state_name: str, context: T) -> None:
        """Log state entry."""
        logger.debug(f"Entering state: {state_name}")

    def on_state_exit(self, state_name: str, context: T) -> None:
        """Log state exit."""
        logger.debug(f"Exiting state: {state_name}")

    def on_error(self, state_name: str, error: Exception, context: T) -> None:
        """Log state error."""
        logger.error(f"Error in state {state_name}: {error}")


class OutputObserver:
    """Sets failure outputs when errors occur."""

    def on_state_enter(self, state_name: str, context: ActionContext) -> None:
        """No action on enter."""
        pass

    def on_state_exit(self, state_name: str, context: ActionContext) -> None:
        """No action on exit."""
        pass

    def on_error(
        self, state_name: str, error: Exception, context: ActionContext
    ) -> None:
        """Set failure output on error."""
        context.set_output(OUTPUT_MIGRATION_STATUS, STATUS_FAILED)
