from utils.miscellaneous import build_image_root_by_id
from utils.fileSystem import get_from_image_root, save_images
from PIL import Image
import os


def igPanoSplit(parameters, session_id):
    # TODO error handling
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    # read parameters
    max_width = parameters['max_width']
    max_height = parameters['max_height']

    new_images = []
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        format = image.format
        width, height = image.size
        if height > max_height:
            # crop image to max_height
            image = image.crop((0, int(height / 2 - (max_height / 2)), width, int(height / 2 + (max_height / 2))))
            new_images.append(image)
        if width > max_width:
            # crop image to max_width
            amount_of_splits = int(width / max_width)
            for i in range(amount_of_splits):
                temp_image = image.crop((int(i * max_width), 0, int((i + 1) * max_width), height))
                new_images.append(temp_image)

    save_images(new_images, new_images[-1].format, session_id)
