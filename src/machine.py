"""Generic State Machine implementation."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Project/Local
from src.logger import setup_logger

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
    """Generic State Machine."""

    def __init__(self, initial_state: State[T], context: T):
        """Initialize state machine.

        Args:
            initial_state: Starting state.
            context: Shared context.
        """
        self.current_state: State[T] | None = initial_state
        self.context = context

    def run(self) -> None:
        """Run the state machine until completion."""
        while self.current_state:
            state_name = self.current_state.__class__.__name__
            logger.debug(f"Entering state: {state_name}")
            
            try:
                next_state = self.current_state.handle(self.context)
                self.current_state = next_state
            except Exception as e:
                logger.error(f"Error in state {state_name}: {e}")
                raise
