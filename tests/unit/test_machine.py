"""Unit tests for the state machine."""

from __future__ import annotations

import pytest

from src.machine import State, StateMachine


# =============================================================================
# TEST STATES
# =============================================================================
class CounterState(State[dict]):
    """Test state that increments counter and transitions."""

    def __init__(self, name: str, next_state: State | None = None):
        self.name = name
        self.next_state = next_state

    def handle(self, context: dict) -> State | None:
        context["count"] = context.get("count", 0) + 1
        context["visited"].append(self.name)
        return self.next_state


class ErrorState(State[dict]):
    """Test state that raises an error."""

    def handle(self, context: dict) -> State | None:
        raise ValueError("Test error")


# =============================================================================
# TESTS
# =============================================================================
def test_state_machine_runs_single_state():
    """Test machine with single terminal state."""
    context = {"count": 0, "visited": []}
    state = CounterState("A")

    machine = StateMachine(initial_state=state, context=context)
    machine.run()

    assert context["count"] == 1
    assert context["visited"] == ["A"]


def test_state_machine_transitions_through_states():
    """Test machine transitions through multiple states."""
    context = {"count": 0, "visited": []}

    state_c = CounterState("C")
    state_b = CounterState("B", next_state=state_c)
    state_a = CounterState("A", next_state=state_b)

    machine = StateMachine(initial_state=state_a, context=context)
    machine.run()

    assert context["count"] == 3
    assert context["visited"] == ["A", "B", "C"]


def test_state_machine_error_propagates():
    """Test machine propagates errors from states."""
    context = {"count": 0, "visited": []}
    state = ErrorState()

    machine = StateMachine(initial_state=state, context=context)

    with pytest.raises(ValueError, match="Test error"):
        machine.run()


def test_state_machine_observer_notified():
    """Test observers are notified on state changes."""

    class TestObserver:
        def __init__(self):
            self.enter_calls = []
            self.exit_calls = []
            self.error_calls = []

        def on_state_enter(self, state_name: str, context: dict) -> None:
            self.enter_calls.append(state_name)

        def on_state_exit(self, state_name: str, context: dict) -> None:
            self.exit_calls.append(state_name)

        def on_error(self, state_name: str, error: Exception, context: dict) -> None:
            self.error_calls.append((state_name, str(error)))

    context = {"count": 0, "visited": []}
    state_b = CounterState("B")
    state_a = CounterState("A", next_state=state_b)

    observer = TestObserver()
    machine = StateMachine(initial_state=state_a, context=context)
    machine.add_observer(observer)
    machine.run()

    assert observer.enter_calls == ["CounterState", "CounterState"]
    assert observer.exit_calls == ["CounterState", "CounterState"]
    assert observer.error_calls == []


def test_state_machine_observer_error_notification():
    """Test observers are notified on errors."""

    class TestObserver:
        def __init__(self):
            self.error_calls = []

        def on_state_enter(self, state_name: str, context: dict) -> None:
            pass

        def on_state_exit(self, state_name: str, context: dict) -> None:
            pass

        def on_error(self, state_name: str, error: Exception, context: dict) -> None:
            self.error_calls.append(state_name)

    context = {}
    state = ErrorState()

    observer = TestObserver()
    machine = StateMachine(initial_state=state, context=context)
    machine.add_observer(observer)

    with pytest.raises(ValueError):
        machine.run()

    assert observer.error_calls == ["ErrorState"]
