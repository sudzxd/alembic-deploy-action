"""Unit tests for commands."""

from __future__ import annotations

import pytest

from src.commands import (
    AnalyzerProtocol,
    ConfigProtocol,
    DryRunCommand,
    ExecutionCommand,
    InitCommand,
    RunnerProtocol,
    SafetyCheckCommand,
)
from src.safety import DangerLevel, SafetyReport


# =============================================================================
# MOCK IMPLEMENTATIONS
# =============================================================================
class MockConfig:
    """Mock configuration satisfying ConfigProtocol."""

    def __init__(
        self,
        command: str = "upgrade",
        revision: str = "head",
        dry_run: bool = False,
        analyze_safety: bool = True,
        fail_on_danger: bool = False,
    ):
        self.command = command
        self.revision = revision
        self.dry_run = dry_run
        self.analyze_safety = analyze_safety
        self.fail_on_danger = fail_on_danger


class MockRunner:
    """Mock runner satisfying RunnerProtocol."""

    def __init__(self) -> None:
        self._current_result = "abc123"
        self._upgrade_result = "CREATE TABLE users;"

    def current(self) -> str:
        return self._current_result

    def upgrade(self, revision: str, sql: bool = False) -> str:
        return self._upgrade_result

    def downgrade(self, revision: str) -> str:
        return ""

    def history(self) -> str:
        return ""

    def show(self, revision: str) -> str:
        return ""


class MockAnalyzer:
    """Mock analyzer satisfying AnalyzerProtocol."""

    def __init__(self, report: SafetyReport | None = None):
        self._report = report or SafetyReport(
            is_safe=True, danger_level=DangerLevel.LOW, warnings=[]
        )

    def analyze(self, sql: str) -> SafetyReport:
        return self._report


class MockContext:
    """Mock context satisfying ActionContextProtocol."""

    def __init__(
        self,
        config: ConfigProtocol | None = None,
        runner: RunnerProtocol | None = None,
        analyzer: AnalyzerProtocol | None = None,
    ):
        self.config: ConfigProtocol = config or MockConfig()
        self.runner: RunnerProtocol = runner or MockRunner()
        self.analyzer: AnalyzerProtocol = analyzer or MockAnalyzer()
        self.outputs: dict[str, str] = {}
        self.sql_preview: str = ""

    def set_output(self, key: str, value: str) -> None:
        self.outputs[key] = value


# =============================================================================
# INIT COMMAND TESTS
# =============================================================================
def test_init_command_sets_revision_outputs():
    """Test InitCommand sets current and target revision outputs."""
    runner = MockRunner()
    runner._current_result = "abc123 (head)"
    context = MockContext(runner=runner)

    InitCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["current-revision"] == "abc123"
    assert context.outputs["target-revision"] == "head"


def test_init_command_handles_empty_revision():
    """Test InitCommand handles empty revision."""
    runner = MockRunner()
    runner._current_result = ""
    context = MockContext(runner=runner)

    InitCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["current-revision"] == "none"


# =============================================================================
# DRY RUN COMMAND TESTS
# =============================================================================
def test_dry_run_command_generates_sql():
    """Test DryRunCommand generates SQL preview."""
    context = MockContext()

    DryRunCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["sql-preview"] == "CREATE TABLE users;"
    assert context.outputs["migration-status"] == "dry-run"
    assert context.sql_preview == "CREATE TABLE users;"


# =============================================================================
# SAFETY CHECK COMMAND TESTS
# =============================================================================
def test_safety_check_command_safe_sql():
    """Test SafetyCheckCommand with safe SQL."""
    analyzer = MockAnalyzer(
        SafetyReport(is_safe=True, danger_level=DangerLevel.LOW, warnings=[])
    )
    context = MockContext(analyzer=analyzer)
    context.sql_preview = "CREATE TABLE users;"

    SafetyCheckCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["is-safe"] == "true"


def test_safety_check_command_dangerous_sql():
    """Test SafetyCheckCommand with dangerous SQL."""
    analyzer = MockAnalyzer(
        SafetyReport(
            is_safe=False,
            danger_level=DangerLevel.HIGH,
            warnings=["DROP TABLE detected"],
        )
    )
    context = MockContext(analyzer=analyzer)
    context.sql_preview = "DROP TABLE users;"

    SafetyCheckCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["is-safe"] == "false"
    assert "DROP TABLE detected" in context.outputs["warnings"]


def test_safety_check_command_fails_on_danger():
    """Test SafetyCheckCommand fails when fail_on_danger is set."""
    config = MockConfig(fail_on_danger=True)
    analyzer = MockAnalyzer(
        SafetyReport(
            is_safe=False,
            danger_level=DangerLevel.HIGH,
            warnings=["DROP TABLE detected"],
        )
    )
    context = MockContext(config=config, analyzer=analyzer)
    context.sql_preview = "DROP TABLE users;"

    with pytest.raises(RuntimeError, match="Dangerous operations"):
        SafetyCheckCommand().execute(context)  # type: ignore[arg-type]


# =============================================================================
# EXECUTION COMMAND TESTS
# =============================================================================
def test_execution_command_upgrade():
    """Test ExecutionCommand runs upgrade."""
    runner = MockRunner()
    context = MockContext(runner=runner)

    ExecutionCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["migration-status"] == "success"


def test_execution_command_downgrade():
    """Test ExecutionCommand runs downgrade."""
    config = MockConfig(command="downgrade", revision="-1")
    context = MockContext(config=config)

    ExecutionCommand().execute(context)  # type: ignore[arg-type]

    assert context.outputs["migration-status"] == "success"


def test_execution_command_unknown_raises():
    """Test ExecutionCommand raises on unknown command."""
    config = MockConfig(command="invalid")
    context = MockContext(config=config)

    with pytest.raises(ValueError, match="Unknown command"):
        ExecutionCommand().execute(context)  # type: ignore[arg-type]
