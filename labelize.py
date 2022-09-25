#!/usr/bin/python3
import os
import shutil
from pathlib import Path

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

def describe_object(image):
    # load an image (into shared CPU/GPU memory)
    img = jetson.utils.loadImage(image)

    # load the recognition network
    net = jetson.inference.imageNet("googlenet")

    # classify the image
    class_idx, confidence = net.Classify(img)

    # find the object description
    class_desc = net.GetClassDesc(class_idx)

    return class_desc

def main():
    folder = "/media/jetson/sony_backup/DCIM/"
    images = find_images_in_folder(folder)
    # images = [os.path.basename(filepath) for filepath in files_in_device]

    for img_filename in images:
        with open(img_filename, 'rb') as img_file:
            img = Image(img_file)
            print(img.get("image_description"))
            if img.get("image_description") is "":
                described = False

        if not described:
            img.image_description = "{'object': '{}'}".format(describe_object(img_filename))
            described = True

        with open(img_filename, 'wb') as new_image_file:
            new_image_file.write(img.get_file())
        break
    
    with open(img_filename, 'rb') as img_file:
        img = Image(img_file)
    
    print(img.has_exif)
    print(sorted(img.list_all()))
    print(f'brightness_value: {img.get("brightness_value")}')
    print(f'Software: {img.get("software")}')
    print(f'orientation: {img.get("orientation")}')
    print(f'image_description: {img.get("image_description")}')

if __name__ == "__main__":
    # execute only if run as a script
    main()