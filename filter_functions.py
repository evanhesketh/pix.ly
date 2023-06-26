from PIL import Image, ImageOps
import io
from utils import create_standardized_image


def b_and_w(file_name, img_to_edit):
    """create new black and white version image"""

    new_file_name = file_name.split('.')
    standardized_image_data = create_standardized_image(
        img_to_edit, new_file_name)
    bw_file_name = f'{new_file_name[0]}-bw.{new_file_name[1]}'
    image = Image.open(standardized_image_data["image"])
    bw_image = ImageOps.grayscale(image=image)

    in_mem_file = io.BytesIO()
    bw_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)

    url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{bw_file_name}"

    return {'url': url, 'file_name': bw_file_name,
            'image': in_mem_file,
            }


def posterize(file_name, img_to_edit):
    """ create new posterized version of image"""

    new_file_name = file_name.split('.')
    standardized_image_data = create_standardized_image(
        img_to_edit, new_file_name)
    pst_file_name = f'{new_file_name[0]}-pst.{new_file_name[1]}'
    image = Image.open(standardized_image_data["image"])
    pst_image = ImageOps.posterize(image=image, bits=2)

    in_mem_file = io.BytesIO()
    pst_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)

    url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{pst_file_name}"

    return {'url': url, 'file_name': pst_file_name,
            'image': in_mem_file
            }
