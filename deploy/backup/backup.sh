#!/usr/bin/env bash
# Backup local (placeholder — implementacao plena na Story 13.4a).
# Story 1.10: so estrutura e pg_dump. Retencao GFS + MinIO mirror vem depois.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${BACKUP_ROOT:-$SCRIPT_DIR/../../_backups}"
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_ROOT"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_USER="${DB_USER:-admin}"
DB_NAME="${DB_NAME:-gestao_vagas_dev}"
export PGPASSWORD="${DB_PASSWORD:-adminpassword}"

DUMP_FILE="$BACKUP_ROOT/pg_${DB_NAME}_${TS}.sql.gz"
echo ">> pg_dump -> $DUMP_FILE"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges \
    | gzip -9 > "$DUMP_FILE"

# TODO Story 13.4a: mirror para MinIO offsite via `mc mirror`.
# mc alias set offsite https://minio.example.com KEY SECRET
# mc cp "$DUMP_FILE" offsite/gv-backups/

echo "OK: $(du -h "$DUMP_FILE" | cut -f1) $DUMP_FILE"
