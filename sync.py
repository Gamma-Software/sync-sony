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

def find_raw_file_in_subfolders(path, filename):
    for root, dirs, filenames in os.walk(path):
        filenames = [os.path.splitext(f)[0] for f in filenames]
        if filename in filenames:
            return os.path.join(root, filename+".ARW")

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
    filepath_to_convert = [find_raw_file_in_subfolders(BACKUP_SOURCE, f) for f in to_convert]

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

backup_camera()
convert_raw()

