import jetson.utils

# load the input image (its pixels will be in the range of 0-255)
imgInput = jetson.utils.loadImage('/app/test/image.jpg')

# allocate the output image, with the same dimensions as input
imgOutput = jetson.utils.cudaAllocMapped(width=imgInput.width, height=imgInput.height, format=imgInput.format)

# normalize the image from [0,255] to [0,1]
jetson.utils.cudaNormalize(imgInput, (0,255), imgOutput, (0,1))