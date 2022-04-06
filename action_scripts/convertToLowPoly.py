# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images

# action specific imports
import triangler
from skimage.io import imread
from PIL import Image
import numpy as np


def convertToLowPoly(parameters, session_id):
    # TODO error handling
    """
       :param parameters: already parsed and checked parameters
       :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]

    # read parameters
    polygons = parameters['polygons']

    new_images = []
    for file in images:
        t = triangler.Triangler(
            sample_method=triangler.SampleMethod.THRESHOLD, points=250)
        img = imread(file)
        img_tri = t.convert(img)
        new_images.append(img_tri)

    # convert ndarrays first to expected format of pillow
    # then to pillow Image format
    # finally save the images
    save_pillow_images([Image.fromarray((image * 255).astype(np.uint8)) for image in new_images],
                       image_format, session_id)

    return 0
