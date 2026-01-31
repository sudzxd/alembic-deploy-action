"""Unit tests for EnvHandler."""

# =============================================================================
# IMPORTS
# =============================================================================
import os

import pytest

from src.env import EnvHandler

# =============================================================================
# TESTS
# =============================================================================

def test_get_str_valid(monkeypatch):
    """Test getting a valid string from env."""
    monkeypatch.setenv("TEST_KEY", "value")
    assert EnvHandler.get_str("TEST_KEY") == "value"

def test_get_str_missing_raises():
    """Test validation error for missing required env var."""
    with pytest.raises(ValueError, match="is required"):
        EnvHandler.get_str("MISSING_KEY")

def test_get_bool_true(monkeypatch):
    """Test boolean parsing."""
    monkeypatch.setenv("BOOL_TRUE", "true")
    monkeypatch.setenv("BOOL_TRUE_CAPS", "TRUE")
    assert EnvHandler.get_bool("BOOL_TRUE") is True
    assert EnvHandler.get_bool("BOOL_TRUE_CAPS") is True

def test_get_bool_false(monkeypatch):
    """Test boolean false parsing."""
    monkeypatch.setenv("BOOL_FALSE", "false")
    monkeypatch.setenv("BOOL_GARBAGE", "random")
    assert EnvHandler.get_bool("BOOL_FALSE") is False
    assert EnvHandler.get_bool("BOOL_GARBAGE") is False  # Default fallback if not "true"

def test_get_int_valid(monkeypatch):
    """Test integer parsing."""
    monkeypatch.setenv("INT_VAL", "123")
    assert EnvHandler.get_int("INT_VAL") == 123

def test_get_int_invalid(monkeypatch):
    """Test invalid integer parsing."""
    monkeypatch.setenv("BAD_INT", "abc")
    with pytest.raises(ValueError, match="must be an integer"):
        EnvHandler.get_int("BAD_INT")
