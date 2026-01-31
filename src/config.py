"""Configuration module for the Alembic Deploy Action."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Libraru
from dataclasses import dataclass

# Project/Local
from src.constants import (
    DEFAULT_ALEMBIC_CONFIG,
    DEFAULT_COMMAND,
    DEFAULT_DRY_RUN,
    DEFAULT_FAIL_ON_DANGER,
    DEFAULT_REVISION,
    DEFAULT_WORKING_DIR,
    ENV_DATABASE_URL,
    INPUT_ALEMBIC_CONFIG,
    INPUT_ANALYZE_SAFETY,
    INPUT_COMMAND,
    INPUT_DATABASE_URL,
    INPUT_DRY_RUN,
    INPUT_FAIL_ON_DANGER,
    INPUT_REVISION,
    INPUT_WORKING_DIRECTORY,
)
from src.env import EnvHandler

# =============================================================================
# CORE CLASSES
# =============================================================================
@dataclass(frozen=True)
class ActionConfig:
    """Configuration for the action derived from inputs.

    Attributes:
        database_url: Connection string for the database.
        command: Alembic command to run (upgrade, downgrade, etc.).
        revision: Target revision for the migration.
        dry_run: Whether to run in dry-run mode (generate SQL only).
        alembic_config_path: Path to the alembic.ini file.
        working_directory: Directory where alembic commands will run.
        analyze_safety: Whether to perform SQL safety analysis.
        fail_on_danger: Whether to fail the action if dangerous ops are found.
    """
    database_url: str
    command: str
    revision: str
    dry_run: bool
    alembic_config_path: str
    working_directory: str
    analyze_safety: bool
    fail_on_danger: bool

    @classmethod
    def from_env(cls) -> ActionConfig:
        """Create configuration from environment variables.

        Returns:
            ActionConfig: Config object populated from environment.

        Raises:
            ValueError: If required environment variables are missing.
        """
        # DATABASE_URL can come from inputs or direct env
        try:
            database_url = EnvHandler.get_str(INPUT_DATABASE_URL)
        except ValueError:
            database_url = EnvHandler.get_str(ENV_DATABASE_URL)

        return cls(
            database_url=database_url,
            command=EnvHandler.get_str(INPUT_COMMAND, default=DEFAULT_COMMAND),
            revision=EnvHandler.get_str(INPUT_REVISION, default=DEFAULT_REVISION),
            dry_run=EnvHandler.get_bool(INPUT_DRY_RUN, default=DEFAULT_DRY_RUN),
            alembic_config_path=EnvHandler.get_str(INPUT_ALEMBIC_CONFIG, default=DEFAULT_ALEMBIC_CONFIG),
            working_directory=EnvHandler.get_str(INPUT_WORKING_DIRECTORY, default=DEFAULT_WORKING_DIR),
            analyze_safety=EnvHandler.get_bool(INPUT_ANALYZE_SAFETY, default="true"),
            fail_on_danger=EnvHandler.get_bool(INPUT_FAIL_ON_DANGER, default=DEFAULT_FAIL_ON_DANGER),
        )
