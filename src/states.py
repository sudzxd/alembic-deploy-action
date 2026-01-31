"""Concrete states for the Alembic action."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

# Project/Local
from src.alembic_ops import AlembicRunner
from src.config import ActionConfig
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
    STATUS_FAILED,
    STATUS_SUCCESS,
)
from src.logger import setup_logger
from src.machine import State
from src.safety import DangerLevel, SafetyAnalyzer

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
        logger.info("Checking current database revision...")
        try:
            current_rev = context.runner.current()
            # Parse output to get just the revision hash if possible
            # Simplified parsing for now
            current_rev_clean = current_rev.strip().split(" ")[0] if current_rev else "none"
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            raise

        context.set_output(OUTPUT_CURRENT_REVISION, current_rev_clean)
        context.set_output(OUTPUT_TARGET_REVISION, context.config.revision)

        logger.info(f"Current revision: {current_rev_clean}")
        logger.info(f"Target revision: {context.config.revision}")

        if context.config.dry_run:
            return DryRunState()
        return ExecutionState()


class DryRunState(State[ActionContext]):
    """Handle Dry-Run execution."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Generate SQL and perform safety analysis."""
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

        if context.config.analyze_safety:
            return SafetyCheckState(sql_content=sql_output)
        
        return None  # End if no safety check needed


class SafetyCheckState(State[ActionContext]):
    """Perform safety analysis on SQL."""

    def __init__(self, sql_content: str):
        self.sql_content = sql_content

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Analyze SQL safety."""
        logger.info("Running Safety Analysis...")
        report = context.analyzer.analyze(self.sql_content)

        if report.warnings:
            logger.warning("SAFETY WARNINGS DETECTED:")
            for warning in report.warnings:
                logger.warning(f"  - {warning}")
            
            context.set_output(OUTPUT_WARNINGS, ";".join(report.warnings))
        
        context.set_output(OUTPUT_IS_SAFE, str(report.is_safe).lower())

        if context.config.fail_on_danger and report.danger_level == DangerLevel.HIGH:
            logger.error("Dangerous operations detected and fail-on-danger is enabled.")
            # We treat this as a failure state
            raise RuntimeError("Dangerous operations detected.")

        if report.is_safe:
            logger.info("No dangerous operations detected.")
        
        return None # End of dry run flow


class ExecutionState(State[ActionContext]):
    """Execute the actual Alembic command."""

    def handle(self, context: ActionContext) -> State[ActionContext] | None:
        """Run the configured command."""
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
            new_rev = context.runner.current().strip().split(" ")[0] if context.runner.current() else "none"
            logger.info(f"New revision: {new_rev}")
        except Exception as e:
            logger.warning(f"Could not fetch new revision: {e}")

        return None
