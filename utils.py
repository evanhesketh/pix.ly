from PIL import ImageOps
import io

def create_small_image(image, file_name):

    """ Takes opened image, file_name. Applies contain method to create
    small version of image.
    Returns dictionary:
    {"file": in_mem_file_small_img, "url": small_url, "file_name": file_name_small} """

    small_image = ImageOps.contain(image, (200, 300))

    in_mem_file_small_img = io.BytesIO()
    small_image.save(in_mem_file_small_img, format="JPEG")
    in_mem_file_small_img.seek(0)

    file_name_small = f"sm-{file_name}"

    small_url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{file_name_small}"
    # small_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{file_name_small}"

    return {"file": in_mem_file_small_img, "url": small_url, "file_name": file_name_small}

def create_large_image(image, file_name):
    """ Takes opened image, file_name. Applies contain method to create
    large version of image.
    Returns dictionary:
    {"file": in_mem_file_large_img, "url": large_url, "file_name": file_name_large} """

    large_image = ImageOps.contain(image, (600, 1000))

    in_mem_file_large_img = io.BytesIO()
    large_image.save(in_mem_file_large_img, format="JPEG")
    in_mem_file_large_img.seek(0)

    file_name_large = f"lg-{file_name}"

    large_url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{file_name_large}"
    # large_url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{file_name_large}"

    return {"file": in_mem_file_large_img, "url": large_url, "file_name": file_name_large}