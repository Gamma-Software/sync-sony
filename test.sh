
BACKUP_SOURCE="/media/jetson/data/sony_backup"

for VARIABLE in $(find $BACKUP_SOURCE/DCIM/*/converted -type d)
do
    if [ "$(basename $VARIABLE)" != "converted" ]; then
        docker run --runtime nvidia -it --rm --network host -v /tmp/.X11-unix/:/tmp/.X11-unix -v /tmp/argus_socket:/tmp/argus_socket -v /etc/enctune.conf:/etc/enctune.conf --device /dev/video0 --volume /media/jetson/data/source/jetson-inference/data:/jetson-inference/data --volume /media/jetson/data/source/jetson-inference/python/training/classification/data:/jetson-inference/python/training/classification/data -v /media/jetson/data/source/jetson-inference/python/training/classification/models:/jetson-inference/python/training/classification/models -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/data:/jetson-inference/python/training/detection/ssd/data -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/models:/jetson-inference/python/training/detection/ssd/models -v $(dirname $VARIABLE):/image labelize python3 /app/labelize_image.py /image
    fi
done