from PIL import Image, ImageOps
import io
from utils import create_large_image, create_small_image


def b_and_w(photo_key, img_to_edit):
    """ create new black and white version of small and large """

    file_name = photo_key.split('.')

    small_image_data = create_small_image(img_to_edit, file_name)
    large_image_data = create_large_image(img_to_edit, file_name)

    bw_small_file_name = f'sm-{file_name[0]}-bw.{file_name[1]}'
    bw_large_file_name = f'lg-{file_name[0]}-bw.{file_name[1]}'

    print("large_file_name", bw_large_file_name)

    small_image = Image.open(small_image_data["file"])
    large_image = Image.open(large_image_data["file"])

    bw_small_image = ImageOps.grayscale(image=small_image)
    bw_large_image = ImageOps.grayscale(image=large_image)

    in_mem_file_small = io.BytesIO()
    bw_small_image.save(in_mem_file_small, format="JPEG")
    in_mem_file_small.seek(0)

    in_mem_file_large = io.BytesIO()
    bw_large_image.save(in_mem_file_large, format="JPEG")
    in_mem_file_large.seek(0)

#     small_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{bw_small_file_name}"
#     large_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{bw_large_file_name}"
    small_url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{bw_small_file_name}"
    large_url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{bw_large_file_name}"

    return {'large_url': large_url, 'small_url': small_url, 'large_file_name': bw_large_file_name,
            'small_file_name': bw_small_file_name, 'large_file': in_mem_file_large,
            'small_file': in_mem_file_small}


def posterize(photo_key, img_to_edit):
    """ create new posterized version of small/large images"""

    file_name = photo_key.split('.')

    small_image_data = create_small_image(img_to_edit, file_name)
    large_image_data = create_large_image(img_to_edit, file_name)

    pst_small_file_name = f'sm-{file_name[0]}-pst.{file_name[1]}'
    pst_large_file_name = f'lg-{file_name[0]}-pst.{file_name[1]}'

    small_image = Image.open(small_image_data["file"])
    large_image = Image.open(large_image_data["file"])

    pst_small_image = ImageOps.posterize(image=small_image, bits=2)
    pst_large_image = ImageOps.posterize(image=large_image, bits=2)

    in_mem_file_small = io.BytesIO()
    pst_small_image.save(in_mem_file_small, format="JPEG")
    in_mem_file_small.seek(0)

    in_mem_file_large = io.BytesIO()
    pst_large_image.save(in_mem_file_large, format="JPEG")
    in_mem_file_large.seek(0)

#     small_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{pst_small_file_name}"
#     large_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{pst_large_file_name}"
    small_url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{pst_small_file_name}"
    large_url = f"https://s3.amazonaws.com/evanhesketh-pix.ly/{pst_large_file_name}"

    return {'large_url': large_url, 'small_url': small_url, 'large_file_name': pst_large_file_name,
            'small_file_name': pst_small_file_name, 'large_file': in_mem_file_large,
            'small_file': in_mem_file_small}



