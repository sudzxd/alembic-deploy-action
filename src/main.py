"""Main entrypoint for the Alembic Deploy Action."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import os
import sys

# Project/Local
from src.alembic_ops import AlembicRunner
from src.config import ActionConfig
from src.constants import OUTPUT_MIGRATION_STATUS, STATUS_FAILED
from src.logger import setup_logger
from src.machine import StateMachine
from src.observers import LoggingObserver, OutputObserver
from src.safety import SafetyAnalyzer
from src.states import ActionContext, InitState

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
logger = setup_logger(__name__)


# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main() -> None:
    """Execute the action logic."""
    try:
        # Load Config
        config = ActionConfig.from_env()

        # Change working directory if needed
        workspace = os.path.abspath(config.working_directory)
        if config.working_directory != ".":
            logger.info(f"Changing working directory to: {workspace}")
            os.chdir(workspace)

        # Setup Environment for Alembic
        os.environ["SQLALCHEMY_DATABASE_URI"] = config.database_url
        os.environ["DATABASE_URL"] = config.database_url

        # Initialize Context
        context = ActionContext(
            config=config,
            runner=AlembicRunner(config.alembic_config_path),
            analyzer=SafetyAnalyzer(),
        )

        # Initialize State Machine with Observers
        machine = StateMachine(initial_state=InitState(), context=context)
        machine.add_observer(LoggingObserver())
        machine.add_observer(OutputObserver())
        machine.run()

    except Exception as e:
        logger.error(f"Action failed: {e}")
        # Build context quickly if possible to output failed status,
        # but simpler to just write to output directly or assume init failed
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"{OUTPUT_MIGRATION_STATUS}={STATUS_FAILED}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
