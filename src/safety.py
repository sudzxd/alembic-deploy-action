"""Safety analysis module for detecting dangerous SQL operations."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import re
from dataclasses import dataclass
from enum import StrEnum

# Project/Local
from src.constants import (
    REGEX_ALTER_COLUMN,
    REGEX_BLOCK_COMMENT,
    REGEX_DROP_COLUMN,
    REGEX_DROP_INDEX,
    REGEX_DROP_TABLE,
    REGEX_LINE_COMMENT,
    REGEX_TRUNCATE,
)

# =============================================================================
# TYPES & CONSTANTS
# =============================================================================
class DangerLevel(StrEnum):
    """Safety danger levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class SafetyReport:
    """Report containing the results of a safety analysis.

    Attributes:
        is_safe: Whether the SQL is considered safe to execute.
        danger_level: The highest danger level detected.
        warnings: List of warning messages detailing detected issues.
    """
    is_safe: bool
    danger_level: DangerLevel
    warnings: list[str]


# =============================================================================
# CORE CLASSES
# =============================================================================
class SafetyAnalyzer:
    """Analyzes SQL for dangerous operations."""

    def analyze(self, sql: str) -> SafetyReport:
        """Analyze SQL content for dangerous operations.

        Args:
            sql: The SQL string to analyze.

        Returns:
            SafetyReport containing the analysis results.
        """
        warnings: list[str] = []
        danger_level = DangerLevel.LOW

        # Remove comments to avoid false positives in comments
        clean_sql = self._strip_comments(sql)

        # Check for DROP TABLE
        if re.search(REGEX_DROP_TABLE, clean_sql, re.IGNORECASE):
            warnings.append("DROP TABLE detected - data will be permanently lost")
            danger_level = DangerLevel.HIGH

        # Check for DROP COLUMN
        if re.search(REGEX_DROP_COLUMN, clean_sql, re.IGNORECASE):
            warnings.append("DROP COLUMN detected - data will be lost")
            if danger_level == DangerLevel.LOW:
                danger_level = DangerLevel.MEDIUM

        # Check for ALTER COLUMN TYPE
        if re.search(REGEX_ALTER_COLUMN, clean_sql, re.IGNORECASE):
            warnings.append("Column type change detected - may fail or lock table")
            if danger_level == DangerLevel.LOW:
                danger_level = DangerLevel.MEDIUM

        # Check for TRUNCATE
        if re.search(REGEX_TRUNCATE, clean_sql, re.IGNORECASE):
            warnings.append("TRUNCATE detected - all data will be deleted")
            danger_level = DangerLevel.HIGH

        # Check for DROP INDEX
        if re.search(REGEX_DROP_INDEX, clean_sql, re.IGNORECASE):
            warnings.append("DROP INDEX detected - may affect query performance")
            # Keeps current danger level (LOW if nothing else found)

        return SafetyReport(
            is_safe=(danger_level == DangerLevel.LOW and not warnings),
            danger_level=danger_level,
            warnings=warnings,
        )

    def _strip_comments(self, sql: str) -> str:
        """Strip SQL comments to reduce false positives.

        Args:
            sql: Raw SQL string.

        Returns:
            SQL string with comments removed.
        """
        # Remove block comments /* */
        sql = re.sub(REGEX_BLOCK_COMMENT, "", sql, flags=re.DOTALL)
        # Remove line comments --
        sql = re.sub(REGEX_LINE_COMMENT, "", sql, flags=re.MULTILINE)
        return sql
