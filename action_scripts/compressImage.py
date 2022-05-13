# default imports for loading and saving images
from PIL import Image
from os import path
from utils.fileSystem import create_temp_dir, get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status


def compressImage(parameters, session_id):
    """
    :param parameters: already parsed and checked parameters
    :param session_id: already validated session id of the user
    """
    status = ExecutionStatus()

    # read parameters
    compression_type = "Lossy"
    compression_rate = parameters['compressionRate']

    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]
    status = ExecutionStatus()

    new_images = []
    temp_folder = create_temp_dir(session_id)
    for file in images:
        try:
            image = Image.open(file)
        except FileNotFoundError:
            status.set_status(Status.FAILURE)
            status.set_message("File not found: " + file)
            return status
        try:
            if compression_type == "Lossy":
                # compress image
                temp_file_name = path.join(temp_folder, path.basename(file))
                image.save(fp=temp_file_name, optimize=True,
                           quality=compression_rate)
                temp_image = Image.open(temp_file_name)
            elif compression_type == 'Lossless':
                status.set_message(
                    "Lossless compression is not supported yet.")
                return status

            new_images.append(temp_image)
        except Exception as e:
            status.set_status(Status.FAILURE)
            status.set_message("Image could not be compressed: " + str(e))
            return status

    save_pillow_images(new_images, image_format, session_id)
    status.set_status(Status.SUCCESS)
    return status
