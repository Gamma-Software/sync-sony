#!/usr/bin/python3
import os
import shutil
from pathlib import Path
import requests

def telegram_bot_sendtext(bot_message):
    bot_token = os.getenv('BOT_TOKEN')
    bot_chatID = os.getenv('BOT_ID')
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def main():
    folder_src = "/mnt/sony/DCIM/"
    folder_dst = "/media/jetson/sony_backup/"
    os.system("rsync -hvrPt --ignore-existing " + folder_src + " " + folder_dst)
    return
#
#    # if Go Pro Not connected
#    if not os.path.exists(folder_src):
#        exit(0)
#
#    # if destination folder doesn't exists create it
#    if not os.path.exists(folder_dst):
#        print("Folder doesn not exists, create it", folder_dst)
#    
#    files_in_device = list(Path(folder_src).rglob(".*.(([mM][pP]4)|(ARW)|[jJ][pP][gG])"))
#    files_backuped = list(Path(folder_dst).rglob(".*.(([mM][pP]4)|(ARW)|[jJ][pP][gG])"))
#
#    filename_in_device = [os.path.basename(filepath) for filepath in files_in_device]
#    filename_backuped = [os.path.basename(filepath) for filepath in files_backuped]
#
#    diff = set(filename_in_device) ^ set(filename_backuped)
#
#    files_to_backup = []
#    for file in diff:
#        for file_in_device in files_in_device:
#            if os.path.basename(file_in_device) in file:
#                files_to_backup.append(file_in_device)
#    
#    if len(diff) > 0:
#        print("Backup Go Pro")
#        backuped = False
#        for file in diff:
#            for file_in_device in files_in_device:
#                if os.path.basename(file_in_device) in file:
#                    src = file_in_device
#                    dst = os.path.join(folder_dst, os.path.basename(file_in_device))
#                    print("Copy: ", src, " -> ", dst)
#                    shutil.copyfile(src, dst)
#                    backuped = True
#        if backuped:
#            print("Les nouvelles video de la device sont disponibles")
#            #telegram_bot_sendtext("Les nouvelles video de la device sont disponibles")
#    else:
#        #telegram_bot_sendtext("La device est branchee mais rien n est a copier")
#        print("No Go Pro files to backup")

if __name__ == "__main__":
    # execute only if run as a script
    main()