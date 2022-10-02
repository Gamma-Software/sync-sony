
BACKUP_SOURCE="/media/jetson/data/sony_backup"


if ! systemctl is-active --quiet sync-sony.service; then
    exit 1
fi