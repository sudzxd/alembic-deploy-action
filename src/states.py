"""Concrete states for the Alembic action."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import os
from dataclasses import dataclass, field

# Project/Local
from src.alembic_ops import AlembicRunner
from src.commands import (
    DryRunCommand,
    ExecutionCommand,
    InitCommand,
    SafetyCheckCommand,
)
from src.config import ActionConfig
from src.logger import setup_logger
from src.machine import State
from src.safety import SafetyAnalyzer

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
logger = setup_logger(__name__)


# =============================================================================
# CONTEXT
# =============================================================================
@dataclass
class ActionContext:
    """Context shared between states."""

    config: ActionConfig
    runner: AlembicRunner
    analyzer: SafetyAnalyzer
    outputs: dict[str, str] = field(default_factory=dict)
    sql_preview: str = ""

    def set_output(self, key: str, value: str) -> None:
        """Set a GitHub Action output."""
        self.outputs[key] = value
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                if "\n" in value:
                    f.write(f"{key}<<EOF\n{value}\nEOF\n")
                else:
                    f.write(f"{key}={value}\n")
        else:
            logger.info(f"[OUTPUT] {key}={value}")


# =============================================================================
# STATES
# =============================================================================
class InitState(State[ActionContext]):
    """Initialization state. Checks connection and setup."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Initialize and validate environment."""
        InitCommand().execute(context)

        if context.config.dry_run:
            return DryRunState()
        return ExecutionState()


class DryRunState(State[ActionContext]):
    """Handle Dry-Run execution."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Generate SQL and perform safety analysis."""
        DryRunCommand().execute(context)

        if context.config.analyze_safety:
            return SafetyCheckState()

        return None


class SafetyCheckState(State[ActionContext]):
    """Perform safety analysis on SQL."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Analyze SQL safety."""
        SafetyCheckCommand().execute(context)
        return None


class ExecutionState(State[ActionContext]):
    """Execute the actual Alembic command."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Run the configured command."""
        ExecutionCommand().execute(context)
        return None
