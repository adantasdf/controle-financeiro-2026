#!/bin/bash
BACKUP_DIR="/home/ubuntu/financeiro/backups"
DB_SRC="/home/ubuntu/financeiro/financas.db"
DATA_HORA=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/financas_${DATA_HORA}.db"

# Cria cópia íntegra usando o comando online do próprio SQLite
sqlite3 "$DB_SRC" ".backup '${BACKUP_FILE}'"

# Garante permissões adequadas
chmod 640 "$BACKUP_FILE"

# POLÍTICA DE RETENÇÃO: Apaga backups com mais de 3 dias (72 horas)
find "$BACKUP_DIR" -type f -name "financas_*.db" -mtime +3 -delete

echo "[$(date)] Backup concluído com sucesso: ${BACKUP_FILE}" >> /home/ubuntu/financeiro/backup.log
