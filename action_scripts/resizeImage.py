# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
from PIL import Image


def resizeImage(parameters, session_id):
    # TODO error handling
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    status = ExecutionStatus()

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
            image = image.crop((point_x, point_y, point_x + width, point_y + height))
        except Exception as e:
            status.set_status("Error: Image could not be resized")
            return status

    save_pillow_images([image], image_format, session_id)
    status.set_status(Status.SUCCESS)
    return status
