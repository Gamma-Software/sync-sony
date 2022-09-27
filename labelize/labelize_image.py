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
described = True

images = find_images_in_folder(folder)
if images:
    net = jetson.inference.detectNet("ssd-mobilenet-v2", sys.argv, 0.5)

for image in images:
    print("Analysing: " + image)
    with open(image, 'rb') as img_file:
        img = Image(img_file)
        # for desc in sorted(img.list_all()):
        #     print(str(desc) + ": " + repr(img.get(desc)))
        if 'image_description' in img.list_all():
            if img.get("image_description").isspace():
                described = False
        else:
            described = False

    if not described:
        detections = detect(net, image)
        img.image_description = "{'object': "+repr(detections)+"}"
        described = True

    with open(image, 'wb') as new_image_file:
        new_image_file.write(img.get_file())