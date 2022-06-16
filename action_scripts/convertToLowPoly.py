# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
import triangler
from skimage.io import imread
from PIL import Image
import numpy as np


def convertToLowPoly(parameters, session_id):
    """
       :param parameters: already parsed and checked parameters
       :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]
    status = ExecutionStatus()

    # read parameters
    polygons = parameters['polygons']

    new_images = []
    t = triangler.Triangler(
        sample_method=triangler.SampleMethod.THRESHOLD, points=polygons)
    for file in images:
        img = imread(file)
        img_tri = t.convert(img)
        new_images.append(img_tri)

    # convert ndarrays first to expected format of pillow
    # then to pillow Image format
    # finally save the images
    save_pillow_images([Image.fromarray((image * 255).astype(np.uint8)) for image in new_images],
                       image_format, session_id)

    status.set_status(Status.SUCCESS)
    return status
