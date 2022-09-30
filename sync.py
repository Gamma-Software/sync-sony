#!/usr/bin/python

BACKUP_SOURCE="/media/jetson/data/sony_backup"
MOUNT_POINT="/mnt/sony/DCIM"

# avoid having parallel script running
import os
import sys
import time
import shutil
import subprocess


def send_notification(msg):
    chat_id="1282108405"
    url = "https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage"
    os.system("curl -s -X POST "+ url + " -d chat_id="+chat_id+" -d text='"+msg+"'")

def filter_files_in_subfolders(path, ext):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(ext):
                files.append(os.path.join(root, f))
    return files

def find_file_in_subfolders(path, filename, ext):
    for root, dirs, filenames in os.walk(path):
        filenames = [os.path.splitext(f)[0] for f in filenames]
        if filename in filenames:
            return os.path.join(root, filename+ext)

def find_folder_in_subfolders(path, foldername):
    for root, dirs, filenames in os.walk(path):
        if foldername in dirs:
            return os.path.join(root, foldername)

def backup_camera():
    print("---- Step: backup camera")
    if not os.system("systemctl is-active --quiet sync-sony.service"):
        print("sync-sony.service is active")
        sys.exit(1)
    
    if not os.system("grep -qs '/mnt/sony ' /proc/mounts"):
        print("The camera is mounted")
        send_notification("Backup sony raw in progress")
        
        # mesure time
        start_time = time.time()

        os.system("rsync -hvrPt --progress --ignore-existing "+MOUNT_POINT+" "+BACKUP_SOURCE)

        elapsed_time = int(time.time() - start_time)
        send_notification("Backup sony raw done in " + str(elapsed_time) + " seconds")
        send_notification("You can unplug your Camera")

        # unmount the camera
        os.system("/bin/systemctl stop mnt-sony.mount")
    else:
        print("The camera is not mounted")

def convert_raw():
    print("---- Step: convert raw")
    # get the list of raw files
    raw_files = filter_files_in_subfolders(BACKUP_SOURCE, ".ARW")
    raw_files = [os.path.splitext(os.path.basename(f))[0] for f in raw_files]
    
    # get the list of converted dng files
    converted_files = filter_files_in_subfolders(BACKUP_SOURCE, ".dng")
    converted_files = [os.path.splitext(os.path.basename(f))[0] for f in converted_files]
    
    # get the list of files to convert
    to_convert = list(set(raw_files) - set(converted_files))
    filepath_to_convert = [find_file_in_subfolders(BACKUP_SOURCE, f, ".ARW") for f in to_convert]

    if len(filepath_to_convert) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Raw image conversion in progress")

        # convert raw to dng
        for f in filepath_to_convert:
            os.system("docker run -v {}:{} raw2dng {}".format(BACKUP_SOURCE, BACKUP_SOURCE, f))

            # check if the converted folder exists
            converted_folder = f.replace(f.split("/")[-1], "converted")
            if not os.path.isdir(converted_folder):
                os.makedirs(converted_folder)
            
            # move the converted file to the converted folder
            shutil.move(f.replace(".ARW", ".dng"), converted_folder)

        elapsed_time = int(time.time() - start_time)
        send_notification("Raw image conversion done in " + str(elapsed_time) + " seconds")

def process_image():
    print("---- Step: process image")
    # get the list of raw files
    raw_converted_files = filter_files_in_subfolders(BACKUP_SOURCE, ".dng")
    raw_converted_files = [os.path.splitext(os.path.basename(f))[0] for f in raw_converted_files]
    
    # get the list of processed dng files
    processed_files = filter_files_in_subfolders(BACKUP_SOURCE, ".jpg")
    processed_files = [os.path.splitext(os.path.basename(f))[0] for f in processed_files]
    
    # get the list of files to convert
    to_process = list(set(raw_converted_files) - set(processed_files))
    filepath_to_convert = [find_file_in_subfolders(BACKUP_SOURCE, f, ".dng") for f in to_process]

    # process raw
    if len(filepath_to_convert) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Raw image processing in progress")

        for f in filepath_to_convert:
            # Create the output folder
            output_folder = f.replace(f.split("/")[-1], "processed")
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            dirname = os.path.dirname(f)
            filename = os.path.basename(f)
            os.system("docker run -v {}:/images process_image python /app/process_image.py /images/{} /images/processed/{}".format(dirname, filename, filename))

        elapsed_time = int(time.time() - start_time)
        send_notification("Raw image processed in " + str(elapsed_time) + " seconds")

def labelize_images():
    print("---- Step: labelize image")
    
    #  find converted folder in backup source
    converted_folders = find_folder_in_subfolders(BACKUP_SOURCE, "converted")

    if len(converted_folders) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Image description in progress")

        for converted_folder in converted_folders:
            os.system("docker run --runtime nvidia -it --rm --network host -v /tmp/.X11-unix/:/tmp/.X11-unix -v /tmp/argus_socket:/tmp/argus_socket -v /etc/enctune.conf:/etc/enctune.conf --device /dev/video0 --volume /media/jetson/data/source/jetson-inference/data:/jetson-inference/data --volume /media/jetson/data/source/jetson-inference/python/training/classification/data:/jetson-inference/python/training/classification/data -v /media/jetson/data/source/jetson-inference/python/training/classification/models:/jetson-inference/python/training/classification/models -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/data:/jetson-inference/python/training/detection/ssd/data -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/models:/jetson-inference/python/training/detection/ssd/models -v {}:/image labelize python3 /app/labelize_image.py /image".format(converted_folder))

        elapsed_time = int(time.time() - start_time)
        send_notification("Image description done " + str(elapsed_time) + " seconds")

def send_to_nas():
    print("---- Step: send to nas")
    return

# backup_camera()
# convert_raw()
# process_image()
labelize_images()
# send_to_nas()

