#!/usr/bin/env fish
# =============================================================================
# backup-db.fish — MariaDB backup via Docker container dump (Fish shell version)
# =============================================================================
#
# WHAT IT DOES
#   1. Reads DB credentials from .env.docker (same file docker-compose uses).
#   2. Locates the running `db` container through docker compose.
#   3. Runs `mysqldump` inside the container and pipes the output through gzip.
#   4. Saves the compressed dump to ./backups/<db>_<YYYYMMDD_HHMMSS>.sql.gz
#   5. Deletes backups older than RETENTION_DAYS (default 30).
#
# USAGE
#   ./backup-db.fish
#
# CRON EXAMPLE  (daily at 02:00, logs to backups/cron.log)
#   0 2 * * * /full/path/backup-db.fish >> /full/path/backups/cron.log 2>&1
#
# DEPENDENCIES
#   docker, docker compose, gzip, find
#
# ENV VARS READ FROM .env.docker
#   MYSQL_USER      — DB user with dump privileges
#   MYSQL_PASSWORD   — password for MYSQL_USER
#   MYSQL_DATABASE   — database name to dump
# =============================================================================

# ── Exit on error ─────────────────────────────────────────────────────────────
# Fish exits on error by default when used in scripts
status is-interactive; and exit 1

# ── Logging helpers ───────────────────────────────────────────────────────────
function _ts
    date +"%Y-%m-%d %H:%M:%S"
end

function log_debug
    echo "["(_ts)"] [DEBUG]   $argv" >&2
end

function log_info
    echo "["(_ts)"] [INFO]    $argv"
end

function log_warning
    echo "["(_ts)"] [WARNING] $argv" >&2
end

function log_error
    echo "["(_ts)"] [ERROR]   $argv" >&2
end

# ── Resolve project root ─────────────────────────────────────────────────────
set -l SCRIPT_DIR (status dirname)
set SCRIPT_DIR (realpath "$SCRIPT_DIR")
log_debug "Script directory: $SCRIPT_DIR"

# ── Load environment ─────────────────────────────────────────────────────────
set -l ENV_FILE "$SCRIPT_DIR/.env.docker"

if not test -f "$ENV_FILE"
    log_error "Environment file not found: $ENV_FILE"
    log_error "Copy .env.docker.example → .env.docker and fill in credentials."
    exit 1
end

# Parse .env.docker manually (Fish doesn't source bash-style env files)
for line in (cat "$ENV_FILE")
    # Skip comments and empty lines
    if string match -qr '^#.*$' "$line"; or test -z "$line"
        continue
    end
    # Extract key=value pairs
    if string match -qr '^[A-Za-z_][A-Za-z0-9_]*=' "$line"
        set -l key (string split -m1 '=' "$line")[1]
        set -l value (string split -m1 '=' "$line")[2]
        # Remove surrounding quotes if present
        set value (string trim -c '"' -c "'" "$value")
        set -gx $key "$value"
    end
end

log_debug "Loaded env from $ENV_FILE (database=$MYSQL_DATABASE, user=$MYSQL_USER)"

# ── Locate the DB container ──────────────────────────────────────────────────
set -l CONTAINER_NAME (docker compose -f "$SCRIPT_DIR/docker-compose.yml" ps -q db 2>/dev/null)

if test -z "$CONTAINER_NAME"
    log_error "The 'db' container is not running."
    log_error "Start it with: docker compose up -d db"
    exit 1
end
log_info "Target container: $CONTAINER_NAME"

# ── Build output path ────────────────────────────────────────────────────────
set -l BACKUP_DIR "$SCRIPT_DIR/backups"
set -l TIMESTAMP (date +"%Y%m%d_%H%M%S")
set -l FILENAME "$MYSQL_DATABASE"_"$TIMESTAMP.sql.gz"
set -l OUTPUT_PATH "$BACKUP_DIR/$FILENAME"
set -l RETENTION_DAYS 30

mkdir -p "$BACKUP_DIR"
log_info "Starting backup → $OUTPUT_PATH"

# ── Dump & compress ─────────────────────────────────────────────────────────
docker exec "$CONTAINER_NAME" \
    mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" \
    --single-transaction --routines --triggers --events \
    "$MYSQL_DATABASE" | gzip > "$OUTPUT_PATH"

# ── Validate dump ────────────────────────────────────────────────────────────
if not test -s "$OUTPUT_PATH"
    log_error "Backup produced an empty file — removing it."
    rm -f "$OUTPUT_PATH"
    exit 1
end

set -l FILE_SIZE (du -h "$OUTPUT_PATH" | string split -f1 '\t')
log_info "Backup created successfully: $FILENAME ($FILE_SIZE)"

# ── Retention cleanup ────────────────────────────────────────────────────────
set -l DELETED_COUNT 0
for old_file in (find "$BACKUP_DIR" -name "$MYSQL_DATABASE"'_*.sql.gz' -mtime +"$RETENTION_DAYS")
    log_debug "Removing expired backup: "(basename "$old_file")
    set DELETED_COUNT (math "$DELETED_COUNT + 1")
    rm -f "$old_file"
end

if test "$DELETED_COUNT" -gt 0
    log_info "Cleaned $DELETED_COUNT backup(s) older than $RETENTION_DAYS days"
else
    log_debug "No expired backups to clean"
end

log_info "Backup job finished"
