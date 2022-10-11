#!/usr/bin/python3

BACKUP_SOURCE="/media/jetson/data/sony_backup"
MOUNT_POINT="/mnt/sony/DCIM"

# avoid having parallel script running
import os
import sys
import time
import shutil
from process.process_image import *


def send_notification(msg):
    chat_id="1282108405"
    url = "https://api.telegram.org/bot5073177948:AAEDeDL7Bi9J-5wYvkXHHQ5_8TiuBybWjFQ/sendMessage"
    os.system("curl -s -X POST "+ url + " -d chat_id="+chat_id+" -d text='"+msg+"' > /dev/null")

def filter_files_in_subfolders(path, ext):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if any(f.endswith(e) for e in ext):
                files.append(os.path.join(root, f))
    return files

def find_file_in_subfolders(path, filename, ext):
    for root, dirs, filenames in os.walk(path):
        filenames = [os.path.splitext(f)[0] for f in filenames]
        if filename in filenames:
            return os.path.join(root, filename+ext)

def find_folders_in_subfolders(path, foldername):
    folders = []
    for root, dirs, filenames in os.walk(path):
        if foldername in dirs:
            folders.append(os.path.join(root, foldername))
    return folders

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

        os.system("rsync -hvrPt --progress --remove-source-files --ignore-existing "+MOUNT_POINT+" "+BACKUP_SOURCE)
        os.chown(BACKUP_SOURCE, 1000, 1000)

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

    #  Convert the dng
    if len(filepath_to_convert) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Raw image conversion ARW to DNG in progress")

        # convert raw to dng
        for f in filepath_to_convert:
            print("    converting {}".format(f))
            
            # Convert arw to dng
            os.system("docker run -v {}:{} raw2dng {}".format(BACKUP_SOURCE, BACKUP_SOURCE, f))
            # check if the converted folder exists
            converted_folder = f.replace(f.split("/")[-1], "converted")
            if not os.path.isdir(converted_folder):
                os.makedirs(converted_folder)
            
            # move the converted file to the converted folder
            shutil.move(f.replace(".ARW", ".dng"), converted_folder)
            
        elapsed_time = int(time.time() - start_time)
        send_notification("Raw image conversion ARW to DNG done in " + str(elapsed_time) + " seconds")
    
    # get the list of converted jpg files
    converted_files_jpg = filter_files_in_subfolders(BACKUP_SOURCE, [".jpg", ".JPG"])
    converted_files_jpg = [os.path.splitext(os.path.basename(f))[0] for f in converted_files_jpg]
    
    # get the list of files to convert
    to_convert = list(set(raw_files) - set(converted_files_jpg))
    filepath_to_convert = [find_file_in_subfolders(BACKUP_SOURCE, f, ".ARW") for f in to_convert]
    
    if len(filepath_to_convert) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Raw image conversion ARW to JPG in progress")

        # convert raw to dng
        for f in filepath_to_convert:
            print("    converting {}".format(f))
            
            # Convert dng to jpg
            os.system("docker run -v {}:{} convert_to_jpg {}".format(BACKUP_SOURCE, BACKUP_SOURCE, f.replace(".ARW", ".dng")))

            # check if the converted folder exists
            converted_folder = f.replace(f.split("/")[-1], "converted")
            if not os.path.isdir(converted_folder):
                os.makedirs(converted_folder)
            
            # move the converted file to the converted folder
            shutil.move(f.replace(".ARW", ".jpg"), converted_folder)

        elapsed_time = int(time.time() - start_time)
        send_notification("Raw image conversion ARW to JPG done in " + str(elapsed_time) + " seconds")


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
    filepath_to_process = [find_file_in_subfolders(BACKUP_SOURCE, f, ".dng") for f in to_process]

    # process raw
    if len(filepath_to_process) > 0:
        # mesure time
        start_time = time.time()
        send_notification("Raw image processing in progress")

        for f in filepath_to_process:
            input_filename = os.path.basename(f)
            output_path = os.path.join(os.path.dirname(f), "converted")
            
            # Create the output folder
            output_folder = f.replace(f.split("/")[-1], "converted")
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            image = cv2.imread(f)
            
            # Process the image
            image_norm = cv2.normalize(image, None, 25, 255, cv2.NORM_MINMAX)
            img = cv2.cvtColor(image_norm, cv2.COLOR_BGR2RGB)
            im_pil = PIL.Image.fromarray(img)
            black_white_process(im_pil).save(os.path.join(output_path, input_filename.replace('.jpg', '_bw.jpg')))
            color_process(im_pil).save(os.path.join(output_path, input_filename.replace('.jpg', '_color.jpg')))

        elapsed_time = int(time.time() - start_time)
        send_notification("Raw image processed in " + str(elapsed_time) + " seconds")

def labelize_images(force=False):
    print("---- Step: labelize image")
    
    #  find converted folder in backup source
    processed_folders = find_folders_in_subfolders(BACKUP_SOURCE, "processed")

    for processed_folder in processed_folders:        
        # Reset the file list if force is True
        if len(sys.argv) > 1 and sys.argv[1] == "True" and os.path.exists(os.path.join(processed_folder, "labelized.txt")):
            os.remove(os.path.join(processed_folder, "labelized.txt"))
        
        # Get the list of images already labeled
        with open(os.path.join(processed_folder, "labelized.txt"), "r+") as labelized:
            images_already_labelized = labelized.read().splitlines()
            
        images_in_folder = filter_files_in_subfolders(processed_folder, "_color.jpg")
        images_in_folder = [f.split("/")[-1] for f in images_in_folder]

        # get the list of images to labelize
        images_to_labelize = list(set(images_in_folder) - set(images_already_labelized))
        
        if len(images_to_labelize) > 0:
            start_time = time.time()
            send_notification("Image description in progress")
            
            os.system("docker run --runtime nvidia -it --rm --network host -v /tmp/.X11-unix/:/tmp/.X11-unix -v /tmp/argus_socket:/tmp/argus_socket -v /etc/enctune.conf:/etc/enctune.conf --device /dev/video0 --volume /media/jetson/data/source/jetson-inference/data:/jetson-inference/data --volume /media/jetson/data/source/jetson-inference/python/training/classification/data:/jetson-inference/python/training/classification/data -v /media/jetson/data/source/jetson-inference/python/training/classification/models:/jetson-inference/python/training/classification/models -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/data:/jetson-inference/python/training/detection/ssd/data -v /media/jetson/data/source/jetson-inference/python/training/detection/ssd/models:/jetson-inference/python/training/detection/ssd/models -v {}:/image labelize python3 /app/labelize_image.py /image".format(processed_folder))

            elapsed_time = int(time.time() - start_time)
            send_notification("Image description done " + str(elapsed_time) + " seconds")

def send_to_nas():
    print("---- Step: send to nas")
    
    #  find converted folder in backup source
    converted_folders = find_folders_in_subfolders(BACKUP_SOURCE, "processed")

    if len(converted_folders) > 0:
        # Then send converted images to NAS
        for converted_folder in converted_folders:
            # Get the files not present on NAS
            files_to_send = os.popen("rsync -vrn --out-format=FILEDETAIL::%n /media/jetson/data/sony_backup/DCIM/101MSDCF/converted/processed valentin@cergy-server.pival.lan:/mnt/backups/main_backup/nextcloud/data/photo_sync/valentin/sony/101MSDCF | grep '^FILEDETAIL'")
            if len(list(files_to_send)) > 0:
                # mesure time
                start_time = time.time()
                send_notification("Send to nas progress")
                print("    sending: " + repr(list(files_to_send)))
                foldername = converted_folder.split("/")[-3]
                os.system("rsync -hvrPt --progress " + converted_folder + " valentin@cergy-server.pival.lan:/mnt/backups/main_backup/nextcloud/data/photo_sync/valentin/sony/"+foldername)
        
                elapsed_time = int(time.time() - start_time)
                send_notification("Send to nas done " + str(elapsed_time) + " seconds")


# backup_camera()
convert_raw()
# process_image()
# labelize_images()
# send_to_nas()

