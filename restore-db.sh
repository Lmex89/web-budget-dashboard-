#!/usr/bin/env bash
# =============================================================================
# restore-db.sh — Restore MariaDB from a gzip-compressed backup
# =============================================================================
#
# WHAT IT DOES
#   1. Reads DB credentials from .env.docker (same file docker-compose uses).
#   2. Locates the running `db` container through docker compose.
#   3. Lists available backups when called with no arguments.
#   4. Prompts for confirmation before overwriting the database.
#   5. Decompresses the chosen .sql.gz and pipes it into `mysql` inside the
#      container, replacing all existing data in the target database.
#
# USAGE
#   ./restore-db.sh                                    # list available backups
#   ./restore-db.sh backups/family_budget_20260715.sql.gz  # restore from file
#
# WARNINGS
#   - This is a DESTRUCTIVE operation. All current data in the database will be
#     replaced by the contents of the backup file.
#   - The script asks for interactive confirmation before proceeding.
#   - When running from cron or CI, pipe `yes` into stdin:
#       yes | ./restore-db.sh backups/family_budget_20260715.sql.gz
#
# DEPENDENCIES
#   docker, docker compose, gunzip
#
# ENV VARS READ FROM .env.docker
#   MYSQL_USER      — DB user with write privileges
#   MYSQL_PASSWORD   — password for MYSQL_USER
#   MYSQL_DATABASE   — target database name
# =============================================================================

# ── Bash strict mode ──────────────────────────────────────────────────────────
# set -e  → exit on error (like Python's unhandled exception)
# set -u  → error on undefined variables (like NameError)
# set -o pipefail → a pipeline fails if ANY command in it fails
set -euo pipefail

# ── Logging helpers ───────────────────────────────────────────────────────────
# Mimic Python loguru levels: DEBUG, INFO, WARNING, ERROR
# Usage: log_info "message"   →  [2026-07-15 02:00:00] [INFO] message
_ts()  { date +"%Y-%m-%d %H:%M:%S"; }
log_debug()   { echo "[$(_ts)] [DEBUG]   $*" >&2; }
log_info()    { echo "[$(_ts)] [INFO]    $*"; }
log_warning() { echo "[$(_ts)] [WARNING] $*" >&2; }
log_error()   { echo "[$(_ts)] [ERROR]   $*" >&2; }

# ── Resolve project root ─────────────────────────────────────────────────────
# SCRIPT_DIR is the directory where this script lives (project root).
# Equivalent to: Path(__file__).resolve().parent in Python.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log_debug "Script directory: ${SCRIPT_DIR}"

# ── Load environment ─────────────────────────────────────────────────────────
# .env.docker is the single source of truth for DB credentials,
# the same file docker-compose.yml loads via env_file.
ENV_FILE="${SCRIPT_DIR}/.env.docker"

if [[ ! -f "$ENV_FILE" ]]; then
  log_error "Environment file not found: ${ENV_FILE}"
  log_error "Copy .env.docker.example → .env.docker and fill in credentials."
  exit 1
fi

# `source` is like Python's exec(open(f).read()) — it evaluates the file
# in the current shell, so MYSQL_USER, MYSQL_PASSWORD, etc. become shell vars.
# shellcheck disable=SC1090
source "$ENV_FILE"
log_debug "Loaded env from ${ENV_FILE} (database=${MYSQL_DATABASE}, user=${MYSQL_USER})"

# ── Locate the DB container ──────────────────────────────────────────────────
# `docker compose ps -q db` returns the container ID of the `db` service.
CONTAINER_NAME=$(docker compose -f "${SCRIPT_DIR}/docker-compose.yml" ps -q db 2>/dev/null)

if [[ -z "$CONTAINER_NAME" ]]; then
  log_error "The 'db' container is not running."
  log_error "Start it with: docker compose up -d db"
  exit 1
fi
log_debug "Target container: ${CONTAINER_NAME}"

# ── List mode: no arguments → show available backups ──────────────────────────
# $# is the argument count (like len(sys.argv) - 1 in Python).
BACKUP_DIR="${SCRIPT_DIR}/backups"

if [[ $# -eq 0 ]]; then
  log_info "Available backups in ${BACKUP_DIR}:"
  echo ""
  # ls -lh gives human-readable sizes; the glob filters to our naming pattern.
  # If no files match, the glob returns the literal string, so we check with -e.
  shopt -s nullglob  # make globs expand to nothing when no match (like glob.glob)
  files=("${BACKUP_DIR}"/${MYSQL_DATABASE}_*.sql.gz)
  shopt -u nullglob

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "  (no backups found)"
  else
    for f in "${files[@]}"; do
      SIZE=$(du -h "$f" | cut -f1)
      MTIME=$(stat -c '%y' "$f" 2>/dev/null | cut -d. -f1)
      echo "  $(basename "$f")  ${SIZE}  ${MTIME}"
    done
  fi

  echo ""
  echo "Usage: $0 <backup-file>"
  echo "Example: $0 backups/${MYSQL_DATABASE}_20260715_020000.sql.gz"
  exit 0
fi

# ── Resolve backup file path ─────────────────────────────────────────────────
# $1 is the first CLI argument (like sys.argv[1] in Python).
BACKUP_FILE="$1"

# If the path is relative (doesn't start with /), make it absolute
# relative to the script directory — not the caller's cwd.
# This makes the script safe to run from cron where cwd may differ.
if [[ ! "$BACKUP_FILE" = /* ]]; then
  BACKUP_FILE="${SCRIPT_DIR}/${BACKUP_FILE}"
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  log_error "Backup file not found: ${BACKUP_FILE}"
  log_error "Run ./restore-db.sh with no arguments to list available backups."
  exit 1
fi

FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log_info "Selected backup: $(basename "$BACKUP_FILE") (${FILE_SIZE})"

# ── Confirmation prompt ──────────────────────────────────────────────────────
# read -rp prints the prompt (-r disables backslash escaping, -p sets prompt).
# ${confirm,,} lowercases the value (like str.lower() in Python).
log_warning "This will OVERWRITE all data in '${MYSQL_DATABASE}'."
read -rp "Continue? [y/N] " confirm
if [[ "${confirm,,}" != "y" ]]; then
  log_info "Aborted by user."
  exit 0
fi

# ── Restore ──────────────────────────────────────────────────────────────────
# gunzip -c  → decompress to stdout (keeps the original .gz file intact)
# docker exec -i  → pass stdin into the container (-i = interactive mode)
# mysql ...  → reads SQL from stdin and executes it
#
# Pipeline:  gunzip → docker exec mysql
# With pipefail, if gunzip fails (corrupt file) the whole pipeline fails.
log_info "Restoring database from: $(basename "$BACKUP_FILE") ..."

gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" \
  mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"

log_info "Restore completed successfully"
log_info "Database '${MYSQL_DATABASE}' now reflects the state from $(basename "$BACKUP_FILE")"
