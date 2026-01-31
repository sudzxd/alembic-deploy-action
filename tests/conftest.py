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
    """Fixture providing a SafetyAnalyzer instance.
    
    Returns:
        SafetyAnalyzer: A SafetyAnalyzer instance.
    """
    return SafetyAnalyzer()

@pytest.fixture
def danger_low() -> DangerLevel:
    """Fixture providing a DangerLevel instance.
    
    Returns:
        DangerLevel: A DangerLevel instance.
    """
    return DangerLevel.LOW

@pytest.fixture
def danger_medium() -> DangerLevel:
    """Fixture providing a DangerLevel instance.
    
    Returns:
        DangerLevel: A DangerLevel instance.
    """
    return DangerLevel.MEDIUM

@pytest.fixture
def danger_high() -> DangerLevel:
    """Fixture providing a DangerLevel instance.
    
    Returns:
        DangerLevel: A DangerLevel instance.
    """
    return DangerLevel.HIGH
