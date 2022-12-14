#!/bin/bash
BACKUP_SOURCE="/media/jetson/data/sony_backup"
MOUNT_POINT="/mnt/sony/DCIM"

START=$(date +%s)

# avoid having parallel script running
if ! systemctl is-active --quiet sync-sony.service; then
    echo "script is already in progress"
    exit 1
fi

#systemctl start mnt-sony.mount
if grep -qs '/mnt/sony ' /proc/mounts; then
    echo "It's mounted."
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup sony raw in progress"
    rsync -hvrPt --progress --ignore-existing "$MOUNT_POINT" "$BACKUP_SOURCE" 
    
    END=$(date +%s)
    DIFF=$(( $END - $START ))
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Backup sony raw done in $DIFF seconds"
    curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="You can unplug your Camera"
    /bin/systemctl stop mnt-sony.mount
else
    echo "The camera is not mounted"
fi

curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image conversion in progress"

# get images not converted yet
RAW_IMAGES=$(find $BACKUP_SOURCE -type f -name "*.ARW" -not -name "*converted*")


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

END=$(date +%s)
DIFF=$(( $END - $START ))
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image conversion done in $DIFF seconds"


curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image processing in progress"
for VARIABLE in $(find $BACKUP_SOURCE/DCIM/* -name '*.dng')
do
    NAME=$(basename $VARIABLE)
    DIR=$(dirname $VARIABLE)
    echo -e "process image $NAME"
    if [ ! -d $DIR/processed ]; then
        mkdir $DIR/processed
    fi
    time docker run -v $DIR:/images process_image python /app/process_image.py /images/$NAME /images/processed/$NAME
done

END=$(date +%s)
DIFF=$(( $END - $START ))
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Raw image processed in $DIFF seconds"


curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Image description in progress"

for VARIABLE in $(find $BACKUP_SOURCE/DCIM/*/converted -type d)
do
    if [ "$(basename $VARIABLE)" != "converted" ]; then
        docker run --runtime nvidia -it --rm --network host -v /tmp/.X11-unix/:/tmp/.X11-unix -v /tmp/argus_socket:/tmp/argus_socket -v /etc/enctune.conf:/etc/enctune.conf --device /dev/video0 --volume /media/jetson/data/source/jetson-inference/data:/jetson-inference/data --volume /media/jetson/data/source/jetson-inference/python/training/classification/data:/jetson-inference/python/training/classification/data -v /media/jetson/data/source/jetson-inference/python/training/classification/models:/jetson-inference/python/training/classification/models -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/data:/jetson-inference/python/training/detection/ssd/data -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/models:/jetson-inference/python/training/detection/ssd/models -v $(dirname $VARIABLE):/image labelize python3 /app/labelize_image.py /image
    fi
done

END=$(date +%s)
DIFF=$(( $END - $START ))
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Image description done in $DIFF seconds"


curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Converted image send to NAS "
# Then send converted images to NAS
for VARIABLE in $(find $BACKUP_SOURCE/DCIM/*/converted -type d)
do
    rsync -hvrPt --progress --ignore-existing $VARIABLE valentin@cergy-server.pival.lan:/mnt/backups/main_backup/nextcloud/data/photo_sync/valentin/sony/$(basename $(dirname $VARIABLE))
done

END=$(date +%s)
DIFF=$(( $END - $START ))
curl -s -X POST https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage -d chat_id=1282108405 -d text="Converted image send to NAS done in $DIFF seconds"
