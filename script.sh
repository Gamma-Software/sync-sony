#!/bin/bash

BACKUP_SOURCE="/media/jetson/sony_backup"
BACKUP_DEVICE="/dev/sony_cam_"
MOUNT_POINT="/media/jetson/sony_cam"

LOGFILE=/var/log/usbautobackup.log
whoami

#check if mount point directory exists, if not create it
if [ ! -d $MOUNT_POINT ] ; then 
    echo "$(date +"%H-%M-%S") : Create backup mounting point folder at $MOUNT_POINT" >> $LOGFILE
	/bin/mkdir  "$MOUNT_POINT"; 
fi

echo "$(date +"%H-%M-%S") : Mount backup device to $MOUNT_POINT" >> $LOGFILE
/bin/mount $BACKUP_DEVICE $MOUNT_POINT

#run a differential backup of files
echo "$(date +"%H-%M-%S") : Backup to $BACKUP_SOURCE" >> $LOGFILE
echo "$(date +"%H-%M-%S") : Unmount backup device" >> $LOGFILE
#/usr/bin/rsync -auz --progress "$MOUNT_POINT/DCIM" "$BACKUP_SOURCE" && /bin/umount "$BACKUP_DEVICE" >> $LOGFILE
exit