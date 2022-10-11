#!/usr/local/bin/python3
import sys
import rawpy
from PIL import Image


file = sys.argv[1]
img = Image.open(file)
with rawpy.imread(file) as raw:
    rgb = raw.postprocess(use_camera_wb=True)
img.save(file.replace("dng", "jpg"), quality=90, subsampling=0)