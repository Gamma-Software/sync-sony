import PIL.Image
from PIL import ImageEnhance, ImageFilter, Image
import rawpy
import sys

file = sys.argv[1]
img = Image.open(file)
with rawpy.imread(file) as raw:
    rgb = raw.postprocess(use_camera_wb=True)

image = PIL.Image.fromarray(rgb)
sharpen = image.filter(ImageFilter.SHARPEN)
applier = ImageEnhance.Contrast(sharpen)
img = applier.enhance(0.9)
filter = ImageEnhance.Sharpness(img)
img = filter.enhance(2)
filter = ImageEnhance.Color(img)
img = filter.enhance(0.9)
img.save(sys.argv[1].replace("dng", "jpg"), quality=100, subsampling=0)
img.save(sys.argv[1].replace("dng", "tiff"))