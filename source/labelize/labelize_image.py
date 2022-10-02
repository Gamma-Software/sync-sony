#!/usr/bin/python3
import os
import shutil
from pathlib import Path
import sys
import jetson.inference
import jetson.utils

# pip install exif
from exif import Image

def detect(net, _image):
    detections = net.Detect(jetson.utils.loadImage(_image))
    objects = []
    for detection in detections:
        _class = net.GetClassDesc(detection.ClassID)
        if _class not in objects:
            objects.append(_class)
    return objects

def filter_files_in_subfolders(path, ext):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(ext):
                files.append(f)
    return files

def find_file_in_subfolders(path, filename):
    for root, dirs, filenames in os.walk(path):
        if filename in filenames:
            return filename

processed_folder = sys.argv[1]

with open(os.path.join(processed_folder, "labelized.txt"), "r") as labelized:
    images_already_labelized = labelized.read().splitlines()
    # images_already_labelized = [f.split("/")[-1] for f in images_already_labelized]
images_in_folder = filter_files_in_subfolders(processed_folder, ".jpg")

# get the list of images to labelize
images_to_labelize = list(set(images_in_folder) - set(images_already_labelized))
images_to_labelize = [find_file_in_subfolders("/image", f) for f in images_to_labelize]

if len(images_to_labelize) > 0:
    net = jetson.inference.detectNet("ssd-mobilenet-v2", sys.argv, 0.5)
    for image in images_to_labelize:
        described = True
        with open(os.path.join(processed_folder, image), 'rb') as img_file:
            img = Image(img_file)
        print("Analysing: " + os.path.join(processed_folder, image))
        detections = detect(net, os.path.join(processed_folder, image))
        img.image_description = "{'object': "+repr(detections)+"}"
        with open(os.path.join(processed_folder, image), 'wb') as new_image_file:
            new_image_file.write(img.get_file())
        with open(os.path.join(processed_folder, "labelized.txt"), "a") as labelized:
            labelized.write(image+"\n")