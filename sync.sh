#!/bin/bash
BACKUP_SOURCE="/media/jetson/sony_backup"
MOUNT_POINT="/mnt/sony/DCIM"

#systemctl start mnt-sony.mount
if grep -qs '/mnt/sony ' /proc/mounts; then
    echo "It's mounted."
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup sony raw in progress"
    bot_message $message
    rsync -hvrPt --progress --ignore-existing "$MOUNT_POINT" "$BACKUP_SOURCE" 
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup sony raw in finished"
    bot_message $message
    /bin/systemctl stop mnt-sony.mount
else
    echo "It's not mounted."
fi


curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image conversion in progress"
find $BACKUP_SOURCE/DCIM/* -name '*.ARW' | xargs -I{} docker run -v $BACKUP_SOURCE:$BACKUP_SOURCE raw2dng {}

# Create the folder converted to the root of the image folder
for VARIABLE in $(find $BACKUP_SOURCE/DCIM/* -type d)
do
   if [ ! -d $VARIABLE/converted ] && [ "$(basename $VARIABLE)" != "converted" ]; then
      mkdir $VARIABLE/converted
   fi
done

# Then move the converted images in the converted folder
for VARIABLE in $(find $BACKUP_SOURCE/DCIM/* -name '*.dng')
do
    dir=$(dirname $VARIABLE)
    mv $VARIABLE $dir/converted
done
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image conversion finished"


curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Converted image send to NAS"
# Then send converted images to NAS
for VARIABLE in $(find $BACKUP_SOURCE/DCIM/*/converted -type d)
do
    rsync -hvrPt --progress --ignore-existing $VARIABLE valentin@cergy-server.pival.lan:/mnt/backups/main_backup/nextcloud/data/photo_sync/valentin/sony/$(basename $(dirname $VARIABLE))
done
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Converted image send to NAS"
