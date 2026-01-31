"""Unit tests for the SafetyAnalyzer module."""

# =============================================================================
# IMPORTS
# =============================================================================

# =============================================================================
# TESTS
# =============================================================================


def test_analyze_clean_sql_is_safe(analyzer, danger_low):
    """Test that safe SQL returns no warnings."""
    sql = "CREATE TABLE users (id INT);"
    report = analyzer.analyze(sql)
    assert report.is_safe
    assert report.danger_level == danger_low
    assert len(report.warnings) == 0


def test_analyze_drop_table_is_high_danger(analyzer, danger_high):
    """Test that DROP TABLE is detected as high danger."""
    sql = "DROP TABLE users;"
    report = analyzer.analyze(sql)
    assert not report.is_safe
    assert report.danger_level == danger_high
    assert "DROP TABLE detected" in report.warnings[0]


def test_analyze_drop_column_is_medium_danger(analyzer, danger_medium):
    """Test that DROP COLUMN is detected as medium danger."""
    sql = "ALTER TABLE users DROP COLUMN email;"
    report = analyzer.analyze(sql)
    assert not report.is_safe
    assert report.danger_level == danger_medium
    assert "DROP COLUMN detected" in report.warnings[0]


def test_analyze_comments_are_ignored(analyzer):
    """Test that dangerous keywords in comments are ignored."""
    sql = """
    -- This is a comment about DROP TABLE
    SELECT * FROM users;
    /* Another comment about TRUNCATE */
    """
    report = analyzer.analyze(sql)
    assert report.is_safe
    assert len(report.warnings) == 0


def test_analyze_truncate_is_high_danger(analyzer, danger_high):
    """Test that TRUNCATE is detected."""
    sql = "TRUNCATE TABLE logs;"
    report = analyzer.analyze(sql)
    assert report.danger_level == danger_high
