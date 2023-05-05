from PIL import Image, ImageOps
import io


def b_and_w (file_name, img_to_edit):

    bw_file_name =  f'{file_name[0]}-bw.{file_name[1]}'

    bw_image = ImageOps.grayscale(image=img_to_edit)

    in_mem_file = io.BytesIO()
    bw_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)
    url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{bw_file_name}"
    # url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{bw_file_name}"

    return { 'url': url, 'edited_file_name': bw_file_name, 'file': in_mem_file}

def posterize (file_name, img_to_edit):

    postr_file_name =  f'{file_name[0]}-pst.{file_name[1]}'

    bw_image = ImageOps.posterize(image=img_to_edit, bits=2)

    in_mem_file = io.BytesIO()
    bw_image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)
    url= f"https://s3.us-west-1.amazonaws.com/kmdeakers-pix.ly/{postr_file_name}"
    # url= f"https://s3.amazonaws.com/evanhesketh-pix.ly/{postr_file_name}"

    return { 'url': url, 'edited_file_name': postr_file_name, 'file': in_mem_file}