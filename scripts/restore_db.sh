#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../.env"

if [ -z "${1:-}" ]; then
    echo "Usage Error: Run the shell command explicitly providing the backup file path location argument target."
    echo "Example: ./scripts/restore_db.sh data/backups/tn_holiday_backup_file.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Target recovery backup archive item target missing: $BACKUP_FILE"
    exit 1
fi

echo "Initiating system structural override reconstruction operations using archive source: $BACKUP_FILE"
gunzip -c "$BACKUP_FILE" | mysql -u"$DB_USER" -p"$DB_PASSWORD" -h"$DB_HOST" --port="$DB_PORT" "$DB_NAME"
echo "System core state sync restoration process finalized successfully."