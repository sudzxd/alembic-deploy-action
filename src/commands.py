"""Command classes for action execution logic."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

# Project/Local
from src.constants import (
    CMD_CURRENT,
    CMD_DOWNGRADE,
    CMD_HISTORY,
    CMD_SHOW,
    CMD_UPGRADE,
    OUTPUT_CURRENT_REVISION,
    OUTPUT_IS_SAFE,
    OUTPUT_MIGRATION_STATUS,
    OUTPUT_SQL_PREVIEW,
    OUTPUT_TARGET_REVISION,
    OUTPUT_WARNINGS,
    STATUS_DRY_RUN,
    STATUS_SUCCESS,
)
from src.logger import setup_logger
from src.safety import DangerLevel, SafetyReport

if TYPE_CHECKING:
    from src.states import ActionContext


# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
logger = setup_logger(__name__)


# =============================================================================
# PROTOCOLS (for testing)
# =============================================================================
class ConfigProtocol(Protocol):
    """Protocol for action configuration."""

    command: str
    revision: str
    dry_run: bool
    analyze_safety: bool
    fail_on_danger: bool


class RunnerProtocol(Protocol):
    """Protocol for Alembic runner."""

    def current(self) -> str: ...
    def upgrade(self, revision: str, sql: bool = False) -> str: ...
    def downgrade(self, revision: str) -> str: ...
    def history(self) -> str: ...
    def show(self, revision: str) -> str: ...


class AnalyzerProtocol(Protocol):
    """Protocol for safety analyzer."""

    def analyze(self, sql: str) -> SafetyReport: ...


@runtime_checkable
class ActionContextProtocol(Protocol):
    """Protocol for action context."""

    config: ConfigProtocol
    runner: RunnerProtocol
    analyzer: AnalyzerProtocol
    sql_preview: str

    def set_output(self, key: str, value: str) -> None: ...


# =============================================================================
# CORE CLASSES
# =============================================================================
class Command(ABC):
    """Abstract base command for execution logic."""

    @abstractmethod
    def execute(self, context: ActionContext) -> None:
        """Execute the command.

        Args:
            context: The shared context object.
        """
        pass


class InitCommand(Command):
    """Initialize and get current database revision."""

    def execute(self, context: ActionContext) -> None:
        """Get current revision and set outputs."""
        logger.info("Checking current database revision...")
        try:
            current_rev = context.runner.current()
            current_rev_clean = (
                current_rev.strip().split(" ")[0] if current_rev else "none"
            )
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            raise

        context.set_output(OUTPUT_CURRENT_REVISION, current_rev_clean)
        context.set_output(OUTPUT_TARGET_REVISION, context.config.revision)

        logger.info(f"Current revision: {current_rev_clean}")
        logger.info(f"Target revision: {context.config.revision}")


class DryRunCommand(Command):
    """Generate SQL preview without executing."""

    def execute(self, context: ActionContext) -> None:
        """Generate SQL and store in context."""
        logger.info("Running in DRY-RUN mode")

        try:
            sql_output = context.runner.upgrade(context.config.revision, sql=True)
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise

        logger.info("Migration Preview:")
        print("==========================================")
        print(sql_output)
        print("==========================================")

        context.set_output(OUTPUT_SQL_PREVIEW, sql_output)
        context.set_output(OUTPUT_MIGRATION_STATUS, STATUS_DRY_RUN)

        # Store for safety check
        context.sql_preview = sql_output


class SafetyCheckCommand(Command):
    """Analyze SQL for dangerous operations."""

    def execute(self, context: ActionContext) -> None:
        """Run safety analysis on generated SQL."""
        logger.info("Running Safety Analysis...")

        sql_content = getattr(context, "sql_preview", "")
        if not sql_content:
            logger.warning("No SQL content to analyze")
            return

        report = context.analyzer.analyze(sql_content)

        if report.warnings:
            logger.warning("SAFETY WARNINGS DETECTED:")
            for warning in report.warnings:
                logger.warning(f"  - {warning}")
            context.set_output(OUTPUT_WARNINGS, ";".join(report.warnings))

        context.set_output(OUTPUT_IS_SAFE, str(report.is_safe).lower())

        if context.config.fail_on_danger and report.danger_level == DangerLevel.HIGH:
            logger.error("Dangerous operations detected and fail-on-danger is enabled.")
            raise RuntimeError("Dangerous operations detected.")

        if report.is_safe:
            logger.info("No dangerous operations detected.")


class ExecutionCommand(Command):
    """Execute the actual Alembic command."""

    def execute(self, context: ActionContext) -> None:
        """Run the configured migration command."""
        cmd = context.config.command
        rev = context.config.revision

        logger.info(f"Executing migration: {cmd} {rev}")

        if cmd == CMD_UPGRADE:
            context.runner.upgrade(rev)
        elif cmd == CMD_DOWNGRADE:
            context.runner.downgrade(rev)
        elif cmd == CMD_CURRENT:
            print(context.runner.current())
        elif cmd == CMD_HISTORY:
            print(context.runner.history())
        elif cmd == CMD_SHOW:
            print(context.runner.show(rev))
        else:
            raise ValueError(f"Unknown command: {cmd}")

        logger.info("Migration operation complete.")
        context.set_output(OUTPUT_MIGRATION_STATUS, STATUS_SUCCESS)

        # Update revision output
        try:
            current = context.runner.current()
            new_rev = current.strip().split(" ")[0] if current else "none"
            logger.info(f"New revision: {new_rev}")
        except Exception as e:
            logger.warning(f"Could not fetch new revision: {e}")
