#!/bin/bash
set -euo pipefail

# ============================================================================
# Alembic Deploy Action - Entrypoint Script
# ============================================================================

# -----------------------------------------------------------------------------
# Configuration & Constants
# -----------------------------------------------------------------------------

readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# -----------------------------------------------------------------------------
# Logging Functions
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# -----------------------------------------------------------------------------
# Validation Functions
# -----------------------------------------------------------------------------

validate_config_file() {
    if [ ! -f "${ALEMBIC_CONFIG}" ]; then
        log_error "Alembic config file not found: ${ALEMBIC_CONFIG}"
        exit 1
    fi
    log_info "Using Alembic config: ${ALEMBIC_CONFIG}"
}

validate_database_connection() {
    if [ -z "${DATABASE_URL}" ]; then
        log_error "DATABASE_URL is not set"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Alembic Operations
# -----------------------------------------------------------------------------

get_current_revision() {
    alembic -c "${ALEMBIC_CONFIG}" current 2>/dev/null | \
        grep -oP '[a-f0-9]{12}' | \
        head -n1 || echo "none"
}

generate_migration_sql() {
    local revision="$1"
    alembic -c "${ALEMBIC_CONFIG}" upgrade "${revision}" --sql 2>&1 || true
}

execute_alembic_command() {
    local command="$1"
    local revision="$2"

    case "${command}" in
        upgrade)
            alembic -c "${ALEMBIC_CONFIG}" upgrade "${revision}"
            ;;
        downgrade)
            alembic -c "${ALEMBIC_CONFIG}" downgrade "${revision}"
            ;;
        current)
            alembic -c "${ALEMBIC_CONFIG}" current
            ;;
        history)
            alembic -c "${ALEMBIC_CONFIG}" history
            ;;
        show)
            alembic -c "${ALEMBIC_CONFIG}" show "${revision}"
            ;;
        *)
            log_error "Unknown command: ${command}"
            exit 1
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Safety Analysis Functions
# -----------------------------------------------------------------------------

detect_dangerous_operations() {
    local sql="$1"
    local warnings=()
    local danger_level="LOW"

    if echo "$sql" | grep -iq "DROP TABLE"; then
        warnings+=("DROP TABLE detected - data will be permanently lost")
        danger_level="HIGH"
    fi

    if echo "$sql" | grep -iq "DROP COLUMN"; then
        warnings+=("DROP COLUMN detected - data will be lost")
        [ "$danger_level" = "LOW" ] && danger_level="MEDIUM"
    fi

    if echo "$sql" | grep -iq "ALTER.*COLUMN.*TYPE"; then
        warnings+=("Column type change detected - may fail or lock table")
        [ "$danger_level" = "LOW" ] && danger_level="MEDIUM"
    fi

    if echo "$sql" | grep -iq "TRUNCATE"; then
        warnings+=("TRUNCATE detected - all data will be deleted")
        danger_level="HIGH"
    fi

    if echo "$sql" | grep -iq "DROP INDEX"; then
        warnings+=("DROP INDEX detected - may affect query performance")
    fi

    echo "${danger_level}|$(IFS=';'; echo "${warnings[*]}")"
}

analyze_sql_safety() {
    local sql="$1"
    local result
    local danger_level
    local warnings_str

    result=$(detect_dangerous_operations "$sql")
    danger_level="${result%%|*}"
    warnings_str="${result#*|}"

    if [ -n "$warnings_str" ] && [ "$warnings_str" != "" ]; then
        echo ""
        log_warning "SAFETY ANALYSIS RESULTS:"

        IFS=';' read -ra warnings <<< "$warnings_str"
        for warning in "${warnings[@]}"; do
            echo "  - $warning"
        done
        echo ""

        # Set GitHub outputs
        {
            echo "warnings<<EOF"
            printf '%s\n' "${warnings[@]}"
            echo "EOF"
        } >> "$GITHUB_OUTPUT"

        echo "is-safe=$([ "$danger_level" = "LOW" ] && echo true || echo false)" >> "$GITHUB_OUTPUT"

        # Fail if configured
        if [ "${FAIL_ON_DANGER}" = "true" ] && [ "$danger_level" = "HIGH" ]; then
            log_error "Dangerous operations detected and fail-on-danger is enabled"
            exit 1
        fi
    else
        log_success "No dangerous operations detected"
        echo "is-safe=true" >> "$GITHUB_OUTPUT"
        echo "warnings=" >> "$GITHUB_OUTPUT"
    fi
}

# -----------------------------------------------------------------------------
# Dry-Run Workflow
# -----------------------------------------------------------------------------

execute_dry_run() {
    local target_revision="$1"

    log_info "Running in DRY-RUN mode (no changes will be made)"

    local sql_output
    sql_output=$(generate_migration_sql "${target_revision}")

    echo ""
    log_info "Migration Preview:"
    echo "=========================================="
    echo "$sql_output"
    echo "=========================================="
    echo ""

    # Save SQL to output
    {
        echo "sql-preview<<EOF"
        echo "$sql_output"
        echo "EOF"
    } >> "$GITHUB_OUTPUT"

    # Analyze safety if enabled
    if [ "${ANALYZE_SAFETY}" = "true" ]; then
        analyze_sql_safety "$sql_output"
    fi

    echo "migration-status=dry-run" >> "$GITHUB_OUTPUT"
    log_success "Dry-run complete"
}

# -----------------------------------------------------------------------------
# Migration Workflow
# -----------------------------------------------------------------------------

execute_migration() {
    local command="$1"
    local target_revision="$2"
    local current_revision="$3"

    log_info "Executing migration: ${command} ${target_revision}"

    execute_alembic_command "${command}" "${target_revision}"

    local new_revision
    new_revision=$(get_current_revision)

    echo ""
    log_success "Migration complete"
    log_info "Previous revision: ${current_revision}"
    log_info "Current revision: ${new_revision}"

    echo "migration-status=success" >> "$GITHUB_OUTPUT"
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
    # Navigate to working directory
    cd "${WORKING_DIR}"

    # Validate environment
    validate_config_file
    validate_database_connection

    # Set database URL for Alembic
    export SQLALCHEMY_DATABASE_URI="${DATABASE_URL}"

    # Get current and target revisions
    log_info "Checking current database revision..."
    local current_rev
    current_rev=$(get_current_revision)

    local target_rev="${ALEMBIC_REVISION}"

    # Set outputs
    echo "current-revision=${current_rev}" >> "$GITHUB_OUTPUT"
    echo "target-revision=${target_rev}" >> "$GITHUB_OUTPUT"

    log_info "Current revision: ${current_rev}"
    log_info "Target revision: ${target_rev}"

    # Execute workflow based on mode
    if [ "${DRY_RUN}" = "true" ]; then
        execute_dry_run "${target_rev}"
    else
        execute_migration "${ALEMBIC_COMMAND}" "${target_rev}" "${current_rev}"
    fi
}

# Execute main function
main
