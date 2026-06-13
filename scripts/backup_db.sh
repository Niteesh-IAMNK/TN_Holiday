#!/usr/bin/env bash
set -euo pipefail

# Ingest configuration mappings directly from workspace environment profiles
source "$(dirname "$0")/../.env"

BACKUP_DIR="$(dirname "$0")/../data/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$BACKUP_DIR/tn_holiday_backup_$TIMESTAMP.sql.gz"

logger -t TN_HOLIDAYS_BACKUP "Starting MariaDB database serialization update script..."

mysqldump -u"$DB_USER" -p"$DB_PASSWORD" -h"$DB_HOST" --port="$DB_PORT" \
    --single-transaction --quick --lock-tables=false "$DB_NAME" | gzip > "$OUTPUT_FILE"

logger -t TN_HOLIDAYS_BACKUP "Database serialization written cleanly onto resource: $OUTPUT_FILE"

# Retention housekeeping rule: Prune backups older than 14 days
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +14 -delete