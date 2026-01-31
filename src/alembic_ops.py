"""Alembic operations module."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import subprocess

# Project/Local
from src.constants import CMD_CURRENT, CMD_DOWNGRADE, CMD_HISTORY, CMD_SHOW, CMD_UPGRADE
from src.logger import setup_logger

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================

# =============================================================================
# LOGGING
# =============================================================================
logger = setup_logger(__name__)


# =============================================================================
# CORE CLASSES
# =============================================================================
class AlembicRunner:
    """Handles execution of Alembic commands."""

    def __init__(self, config_path: str):
        """Initialize Runner.

        Args:
            config_path: Path to alembic.ini
        """
        self.config_path = config_path

    def upgrade(self, revision: str = "head", sql: bool = False) -> str:
        """Run alembic upgrade.

        Args:
            revision: Target revision.
            sql: If True, return generated SQL instead of executing.

        Returns:
            Output from alembic command (logs or SQL).
        """
        cmd = ["alembic", "-c", self.config_path, CMD_UPGRADE, revision]
        if sql:
            cmd.append("--sql")
        return self._run_command(cmd)

    def downgrade(self, revision: str, sql: bool = False) -> str:
        """Run alembic downgrade.

        Args:
            revision: Target revision.
            sql: If True, return generated SQL.

        Returns:
            Output from command.
        """
        cmd = ["alembic", "-c", self.config_path, CMD_DOWNGRADE, revision]
        if sql:
            cmd.append("--sql")
        return self._run_command(cmd)

    def current(self) -> str:
        """Get current revision.

        Returns:
            Output from current command.
        """
        return self._run_command(["alembic", "-c", self.config_path, CMD_CURRENT])

    def history(self) -> str:
        """Show migration history.

        Returns:
            Output from history command.
        """
        return self._run_command(["alembic", "-c", self.config_path, CMD_HISTORY])

    def show(self, revision: str) -> str:
        """Show details of a revision.

        Returns:
            Output from show command.
        """
        return self._run_command(["alembic", "-c", self.config_path, CMD_SHOW, revision])

    def _run_command(self, cmd: list[str]) -> str:
        """Execute subprocess command.

        Args:
            cmd: Command list to execute.

        Returns:
            Standard output/error combined.

        Raises:
            subprocess.CalledProcessError: If command fails.
        """
        logger.info(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            raise
