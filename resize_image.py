import PIL
from PIL import Image


def resize_image(input_image_path,
                 output_image_path,
                 basewidth):
    img = Image.open(input_image_path)

    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save(output_image_path)

# resize_image(input_image_path='caterpillar.jpg', output_image_path='caterpillar.jpg',
#              size=(800, 400))
