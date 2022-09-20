#!/bin/bash
BACKUP_SOURCE="/media/jetson/sony_backup"
MOUNT_POINT="/mnt/sony/DCIM"

#systemctl start mnt-sony.mount
if grep -qs '/mnt/sony ' /proc/mounts; then
    echo "It's mounted."
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup des images en cours"
    bot_message $message
    rsync -hvrPt --progress --ignore-existing "$MOUNT_POINT" "$BACKUP_SOURCE" 
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup des images terminé"
    bot_message $message
    /bin/systemctl stop mnt-sony.mount
else
    echo "It's not mounted."
fi