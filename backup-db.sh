#!/usr/bin/env bash
# =============================================================================
# backup-db.sh — MariaDB backup via Docker container dump
# =============================================================================
#
# WHAT IT DOES
#   1. Reads DB credentials from .env.docker (same file docker-compose uses).
#   2. Locates the running `db` container through docker compose.
#   3. Runs `mysqldump` inside the container and pipes the output through gzip.
#   4. Saves the compressed dump to ./backups/<db>_<YYYYMMDD_HHMMSS>.sql.gz
#   5. Uploads the dump to a Backblaze B2 bucket via rclone (best-effort).
#   6. Prunes cloud backups older than RETENTION_DAYS (mirrors local cleanup).
#   7. Deletes local backups older than RETENTION_DAYS (default 30).
#
# USAGE
#   ./backup-db.sh
#
# CRON EXAMPLE  (daily at 02:00, logs to backups/cron.log)
#   0 2 * * * /full/path/backup-db.sh >> /full/path/backups/cron.log 2>&1
#
# DEPENDENCIES
#   docker, docker compose, gzip, find, rclone (rclone only needed for the
#   Backblaze B2 upload — without it the local backup still succeeds)
#
# ENV VARS READ FROM .env.docker
#   MYSQL_USER         — DB user with dump privileges
#   MYSQL_PASSWORD     — password for MYSQL_USER
#   MYSQL_DATABASE     — database name to dump
#   BACK_BLAZE_KEY_ID  — B2 Application Key ID (rclone account; required to upload)
#   BACK_BLAZE_SECRET   — B2 Application Key (rclone key; required to upload)
#   BACK_BLAZE_BUCKET   — B2 bucket name (default: lmex-backups-db)
#   BACK_BLAZE_DIR      — folder/prefix inside the bucket (default: web-budget-family)
# =============================================================================

# ── Bash strict mode ──────────────────────────────────────────────────────────
# set -e  → exit on error (like Python's unhandled exception)
# set -u  → error on undefined variables (like NameError)
# set -o pipefail → a pipeline fails if ANY command in it fails
#                   (without this, only the LAST command's exit code matters)
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
# This is more reliable than hardcoding the container name.
CONTAINER_NAME=$(docker compose -f "${SCRIPT_DIR}/docker-compose.yml" ps -q db 2>/dev/null)

if [[ -z "$CONTAINER_NAME" ]]; then
  log_error "The 'db' container is not running."
  log_error "Start it with: docker compose up -d db"
  exit 1
fi
log_info "Target container: ${CONTAINER_NAME}"

# ── Build output path ────────────────────────────────────────────────────────
BACKUP_DIR="${SCRIPT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${MYSQL_DATABASE}_${TIMESTAMP}.sql.gz"
OUTPUT_PATH="${BACKUP_DIR}/${FILENAME}"
RETENTION_DAYS=30

# mkdir -p → create directory (and parents) if it doesn't exist;
#            no error if it already exists.  Like os.makedirs(..., exist_ok=True)
mkdir -p "$BACKUP_DIR"
log_info "Starting backup → ${OUTPUT_PATH}"

# ── Dump & compress ─────────────────────────────────────────────────────────
# mysqldump flags:
#   --single-transaction  → consistent snapshot without locking tables
#                           (uses REPEATABLE READ; safe for InnoDB)
#   --routines            → include stored procedures & functions
#   --triggers            → include triggers
#   --events              → include event scheduler events
#
# The pipe: mysqldump stdout → gzip stdin → compressed file
# Because of `set -o pipefail`, if mysqldump fails the whole pipeline fails.
docker exec "$CONTAINER_NAME" \
  mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" \
  --single-transaction --routines --triggers --events \
  "$MYSQL_DATABASE" | gzip > "$OUTPUT_PATH"

# ── Validate dump ────────────────────────────────────────────────────────────
# -s checks the file exists AND has size > 0 (like Path.stat().st_size > 0).
if [[ -s "$OUTPUT_PATH" ]]; then
  FILE_SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)
  log_info "Backup created successfully: ${FILENAME} (${FILE_SIZE})"
else
  log_error "Backup produced an empty file — removing it."
  rm -f "$OUTPUT_PATH"
  exit 1
fi

# ── Backblaze B2 cloud upload (best-effort) ──────────────────────────────────
# upload_to_backblaze copies the compressed dump to the configured B2 bucket and
# prunes cloud backups older than RETENTION_DAYS. If rclone is not installed or
# the B2 credentials are missing, the local backup is still kept and a warning
# is logged (the backup job must never fail because the cloud step did).
upload_to_backblaze() {
  local cloud_dir="${BACK_BLAZE_BUCKET:-lmex-backups-db}/${BACK_BLAZE_DIR:-web-budget-family}"

  if ! command -v rclone >/dev/null 2>&1; then
    log_warning "rclone not found — skipping Backblaze B2 upload (install it: https://rclone.org/install/)"
    return 0
  fi

  if [[ -z "${BACK_BLAZE_KEY_ID:-}" || -z "${BACK_BLAZE_SECRET:-}" ]]; then
    log_warning "BACK_BLAZE_KEY_ID / BACK_BLAZE_SECRET not set in .env.docker — skipping Backblaze B2 upload"
    return 0
  fi

  # rclone resolves the `b2` remote from the `:b2:` shorthand; credentials are
  # passed as CLI flags (older rclone builds ignore the RCLONE_CONFIG_B2_* env
  # vars, so flags are the reliable cross-version approach).
  log_info "Uploading backup to Backblaze B2 → b2:${cloud_dir}/${FILENAME}"
  if rclone copy "$OUTPUT_PATH" ":b2:${cloud_dir}/" \
      --b2-account "$BACK_BLAZE_KEY_ID" \
      --b2-key "$BACK_BLAZE_SECRET"; then
    log_info "Cloud upload succeeded: ${FILENAME}"
  else
    log_error "Cloud upload failed — local backup kept at ${OUTPUT_PATH}"
  fi

  # Prune cloud backups older than RETENTION_DAYS (mirrors local cleanup below).
  log_info "Pruning B2 backups older than ${RETENTION_DAYS} days"
  rclone delete ":b2:${cloud_dir}/" \
      --b2-account "$BACK_BLAZE_KEY_ID" \
      --b2-key "$BACK_BLAZE_SECRET" \
      --include "*.sql.gz" --min-age "${RETENTION_DAYS}d" \
    || log_warning "Cloud retention cleanup failed — cloud backups kept"
}

upload_to_backblaze

# ── Retention cleanup ────────────────────────────────────────────────────────
# `find ... -mtime +N -delete` removes files modified more than N days ago.
# Think of it as: Path.glob("*.sql.gz") filtered by mtime > now - 30 days.
DELETED_COUNT=0
while IFS= read -r old_file; do
  log_debug "Removing expired backup: $(basename "$old_file")"
  DELETED_COUNT=$((DELETED_COUNT + 1))
done < <(find "$BACKUP_DIR" -name "${MYSQL_DATABASE}_*.sql.gz" -mtime +"$RETENTION_DAYS" -print -delete)

if [[ "$DELETED_COUNT" -gt 0 ]]; then
  log_info "Cleaned ${DELETED_COUNT} backup(s) older than ${RETENTION_DAYS} days"
else
  log_debug "No expired backups to clean"
fi

log_info "Backup job finished"
