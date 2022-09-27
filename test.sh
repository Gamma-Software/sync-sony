
BACKUP_SOURCE="/media/jetson/data/sony_backup"

for VARIABLE in $(find $BACKUP_SOURCE/DCIM/* -name '*.dng')
do
    NAME=$(basename $VARIABLE)
    DIR=$(dirname $VARIABLE)
    time docker run -v $DIR:/images process_image python /app/process_image.py /images/$NAME 
done