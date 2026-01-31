"""Centralized constants for the application."""

from __future__ import annotations

# =============================================================================
# LOGGING
# =============================================================================
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# =============================================================================
# DEFAULT VALUES
# =============================================================================
DEFAULT_ALEMBIC_CONFIG = "alembic.ini"
DEFAULT_WORKING_DIR = "."
DEFAULT_REVISION = "head"
DEFAULT_COMMAND = "upgrade"
DEFAULT_DRY_RUN = "false"
DEFAULT_ANALYZE_SAFETY = "true"
DEFAULT_FAIL_ON_DANGER = "false"

# =============================================================================
# ENV VARIABLES
# =============================================================================
INPUT_DATABASE_URL = "INPUT_DATABASE_URL"
ENV_DATABASE_URL = "DATABASE_URL"
ENV_SQLALCHEMY_URL = "SQLALCHEMY_DATABASE_URI"

INPUT_COMMAND = "INPUT_COMMAND"
INPUT_REVISION = "INPUT_REVISION"
INPUT_DRY_RUN = "INPUT_DRY_RUN"
INPUT_ALEMBIC_CONFIG = "INPUT_ALEMBIC_CONFIG"
INPUT_WORKING_DIRECTORY = "INPUT_WORKING_DIRECTORY"
INPUT_ANALYZE_SAFETY = "INPUT_ANALYZE_SAFETY"
INPUT_FAIL_ON_DANGER = "INPUT_FAIL_ON_DANGER"

GITHUB_OUTPUT = "GITHUB_OUTPUT"

# =============================================================================
# OUTPUT KEYS
# =============================================================================
OUTPUT_MIGRATION_STATUS = "migration-status"
OUTPUT_CURRENT_REVISION = "current-revision"
OUTPUT_TARGET_REVISION = "target-revision"
OUTPUT_SQL_PREVIEW = "sql-preview"
OUTPUT_WARNINGS = "warnings"
OUTPUT_IS_SAFE = "is-safe"

# =============================================================================
# COMMANDS
# =============================================================================
CMD_UPGRADE = "upgrade"
CMD_DOWNGRADE = "downgrade"
CMD_CURRENT = "current"
CMD_HISTORY = "history"
CMD_SHOW = "show"

# =============================================================================
# STATUS VALUES
# =============================================================================
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_DRY_RUN = "dry-run"

# =============================================================================
# REGEX PATTERNS
# =============================================================================
REGEX_DROP_TABLE = r"DROP\s+TABLE"
REGEX_DROP_COLUMN = r"DROP\s+COLUMN"
REGEX_ALTER_COLUMN = r"ALTER\s+.*COLUMN.*TYPE"
REGEX_TRUNCATE = r"TRUNCATE"
REGEX_DROP_INDEX = r"DROP\s+INDEX"
REGEX_BLOCK_COMMENT = r"/\*.*?\*/"
REGEX_LINE_COMMENT = r"--.*$"
