from utils.miscellaneous import build_image_root_by_id
from utils.fileSystem import get_from_image_root, save_images
from PIL import Image
import os


def changeFormat(parameters, session_id):
    # TODO error handling
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    # read parameters
    convert_format = parameters['format']
    fill_color = parameters['fillcolor']['red'],\
                 parameters['fillcolor']['green'],\
                 parameters['fillcolor']['blue']

    new_images = []
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        new_image_name = file.split('.')[0] + '.' + convert_format

        if convert_format == 'JPEG':
            image = image.convert("RGBA")
            if image.mode in ('RGBA', 'LA'):
                im_background = Image.new(image.mode[:-1], image.size, fill_color)
                im_background.paste(image, image.split()[-1])
                image = im_background
            new_images.append(image.convert("RGB"))
        elif convert_format == 'PNG':
            new_image_name.append(image.convert("RGBA"))

    save_images(new_images, convert_format, session_id)
