#!/usr/bin/python3
import os
import shutil
from pathlib import Path
import sys
import jetson.inference
import jetson.utils

# pip install exif
from exif import Image

def find_images_in_folder(folder, images = []):
    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isdir(f):
            images.extend(find_images_in_folder(f, images))
        elif f.split(".")[-1] in ["JPG", "jpg"] :
            images.append(f)
    return images

def detect(net, _image):
    detections = net.Detect(jetson.utils.loadImage(_image))
    objects = []
    for detection in detections:
        _class = net.GetClassDesc(detection.ClassID)
        if _class not in objects:
            objects.append(_class)
    return objects

folder = sys.argv[1]
force = True if len(sys.argv) > 2 and sys.argv[2] == "True" else False

images = find_images_in_folder(folder)
if len(images) > 0:
    net = jetson.inference.detectNet("ssd-mobilenet-v2", sys.argv, 0.5)
    for image in images:
        described = True
        with open(image, 'rb') as img_file:
            img = Image(img_file)
            if 'image_description' in img.list_all():
                if img.get("image_description").isspace():
                    described = False
            else:
                described = False
        if not described or force == True:
            print("Analysing: " + image)
            detections = detect(net, image)
            img.image_description = "{'object': "+repr(detections)+"}"
            with open(image, 'wb') as new_image_file:
                new_image_file.write(img.get_file())