"""Unit tests for observers."""

from __future__ import annotations

import logging

from src.observers import LoggingObserver


def test_logging_observer_on_state_enter(caplog):
    """Test LoggingObserver logs on state enter."""
    observer = LoggingObserver()
    context = {}

    caplog.set_level(logging.DEBUG, logger="src.observers")
    observer.on_state_enter("TestState", context)

    assert "Entering state: TestState" in caplog.text


def test_logging_observer_on_state_exit(caplog):
    """Test LoggingObserver logs on state exit."""
    observer = LoggingObserver()
    context = {}

    caplog.set_level(logging.DEBUG, logger="src.observers")
    observer.on_state_exit("TestState", context)

    assert "Exiting state: TestState" in caplog.text


def test_logging_observer_on_error(caplog):
    """Test LoggingObserver logs on error."""
    observer = LoggingObserver()
    context = {}
    error = ValueError("Test error")

    caplog.set_level(logging.ERROR, logger="src.observers")
    observer.on_error("TestState", error, context)

    assert "Error in state TestState" in caplog.text
