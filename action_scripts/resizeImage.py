# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
import logging

# action specific imports
from PIL import Image


def resizeImage(parameters, session_id):
    # TODO error handling
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)

    # read parameters
    cutout = parameters['cutout']
    width = cutout['width']
    height = cutout['height']
    point_x = cutout['positionX']
    point_y = cutout['positionY']
    for file in images:
        image_format = file.split('.')[-1]
        image = Image.open(file)

        try:
            image = image.crop(
                (point_x, point_y, point_x + width, point_y + height))
            save_pillow_images([image], image_format, session_id)
        except Exception as e:
            print("Error: Image could not be resized")
            logging.critical(e)
            return -1
    return 0
