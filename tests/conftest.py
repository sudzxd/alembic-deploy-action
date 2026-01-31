"""Pytest fixtures for the Alembic Deploy Action."""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import pytest

# Project/Local
from src.safety import DangerLevel, SafetyAnalyzer

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def analyzer() -> SafetyAnalyzer:
    """Fixture providing a SafetyAnalyzer instance."""
    return SafetyAnalyzer()


@pytest.fixture
def danger_low() -> DangerLevel:
    """Fixture providing DangerLevel.LOW."""
    return DangerLevel.LOW


@pytest.fixture
def danger_medium() -> DangerLevel:
    """Fixture providing DangerLevel.MEDIUM."""
    return DangerLevel.MEDIUM


@pytest.fixture
def danger_high() -> DangerLevel:
    """Fixture providing DangerLevel.HIGH."""
    return DangerLevel.HIGH
