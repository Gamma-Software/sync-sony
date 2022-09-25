
BACKUP_SOURCE="/media/jetson/sony_backup"

for VARIABLE in $(find $BACKUP_SOURCE/DCIM/*/converted -type d)
do
    rsync -hvrPt --progress --ignore-existing $VARIABLE valentin@cergy-server.pival.lan:/mnt/backups/main_backup/nextcloud/data/photo_sync/valentin/sony/$(basename $(dirname $VARIABLE))
done