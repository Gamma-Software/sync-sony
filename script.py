#!/usr/bin/python3
import os
import shutil
from pathlib import Path

def main():
    folder_src = "/media/jetson/sony_cam"
    folder_dst = "/mnt/data/shares/data/gopro"

    # if Go Pro Not connected
    if not os.path.exists(folder_src):
        exit(0)

    # if destination folder doesn't exists create it
    if not os.path.exists(folder_dst):
        print("Folder does not exists, create it", folder_dst)
    
    files_in_device = list(Path(folder_src).rglob("*.(([mM][pP]4)|(jpe?g))"))
    files_backuped = list(Path(folder_dst).rglob("*.(([mM][pP]4)|(jpe?g))"))

    filename_in_device = [os.path.basename(filepath) for filepath in files_in_device]
    filename_backuped = [os.path.basename(filepath) for filepath in files_backuped]

    diff = set(filename_in_device) ^ set(filename_backuped)

    files_to_backup = []
    for file in diff:
        for file_in_device in files_in_device:
            if os.path.basename(file_in_device) in file:
                files_to_backup.append(file_in_device)
    
    if len(diff) > 0:
        print("Backup Go Pro")
        for file in diff:
            for file_in_device in files_in_device:
                if os.path.basename(file_in_device) in file:
                    src = file_in_device
                    dst = os.path.join(folder_dst, os.path.basename(file_in_device))
                    print("Copy: ", src, " -> ", dst)
                    shutil.copyfile(src, dst)
    else:
        print("No Go Pro files to backup")

if __name__ == "__main__":
    # execute only if run as a script
    main()