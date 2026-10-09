#!/bin/bash
# FinSight Backup Script
# Creates backups of PostgreSQL and MongoDB

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-finsight-postgres}"
MONGO_CONTAINER="${MONGO_CONTAINER:-finsight-mongodb}"

mkdir -p "$BACKUP_DIR"

echo "Starting backup at $(date)"

# PostgreSQL backup
echo "Backing up PostgreSQL..."
docker exec "$POSTGRES_CONTAINER" pg_dump -U finsight_user finsight > "$BACKUP_DIR/postgres_$DATE.sql"
echo "PostgreSQL backup saved to $BACKUP_DIR/postgres_$DATE.sql"

# MongoDB backup
echo "Backing up MongoDB..."
docker exec "$MONGO_CONTAINER" mongodump --uri="mongodb://admin:admin_password@localhost:27017/finsight_analytics?authSource=admin" --out="/data/backup_$DATE"
docker cp "$MONGO_CONTAINER:/data/backup_$DATE" "$BACKUP_DIR/mongo_$DATE"
echo "MongoDB backup saved to $BACKUP_DIR/mongo_$DATE"

# Compress
echo "Compressing backups..."
tar -czf "$BACKUP_DIR/finsight_backup_$DATE.tar.gz" -C "$BACKUP_DIR" "postgres_$DATE.sql" "mongo_$DATE"
rm -rf "$BACKUP_DIR/postgres_$DATE.sql" "$BACKUP_DIR/mongo_$DATE"
echo "Compressed backup saved to $BACKUP_DIR/finsight_backup_$DATE.tar.gz"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "finsight_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed at $(date)"
echo "Backup location: $BACKUP_DIR/finsight_backup_$DATE.tar.gz"