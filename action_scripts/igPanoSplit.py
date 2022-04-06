# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images

# action specific imports
from PIL import Image


# TODO error handling
# TODO improve behaviour
def igPanoSplit(parameters, session_id):
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]

    # read parameters
    max_width = parameters['max_width']
    max_height = parameters['max_height']

    new_images = []
    for file in images:
        image = Image.open(file)
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

    save_pillow_images(new_images, image_format, session_id)
