# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
from PIL import Image


def igPanoSplit(parameters, session_id):
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]
    status = ExecutionStatus()

    # read parameters
    images_parameter = parameters['images']
    start_pos_x = images_parameter["positionX"]
    start_pos_y = images_parameter['positionY']
    width = images_parameter['width']
    height = images_parameter['height']
    areas = images_parameter['areas']

    new_images = []
    for file in images:
        try:
            image = Image.open(file)
        except FileNotFoundError:
            status.set_status(Status.FAILURE)
            status.set_message("File not found: " + file)
            return status
        iteration = 0
        current_width, current_height = image.size
        while iteration < areas:
            used_width = start_pos_x + (width * (iteration + 1))
            if current_width < used_width:
                width = current_width - (used_width - width)
                # set iteration beyond the last area
                iteration = areas

            current_start_pos_x = start_pos_x + (width * iteration)
            new_image = image.crop((current_start_pos_x, start_pos_y, current_start_pos_x + width, start_pos_y + height))
            new_images.append(new_image)
            # increment iteration
            iteration += 1

    save_pillow_images(new_images, image_format, session_id)

    status.set_status(Status.SUCCESS)
    return status
