from PIL import ImageOps
import io

def create_standardized_image(image, file_name):
    """Takes opened image, file_name.
    Applies contain method to create standardized version of image.
    Returns dictionary:
    {"file": in_mem_file_large_img, "url": large_url, "file_name": file_name_large}"""

    standardized_image = ImageOps.contain(image, (600, 1000))

    in_mem_file = io.BytesIO()
    standardized_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)

    url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{file_name}"

    return {"image": in_mem_file, "url": url, "file_name": file_name}