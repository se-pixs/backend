from utils.miscellaneous import build_image_root_by_id
from utils.fileSystem import get_from_image_root, orderly_clear_images
import triangler
from skimage.io import imread
import matplotlib.pyplot as plt
import os


def convertToLowPoly(parameters, session_id):
    # TODO error handling
    """
       :param parameters: already parsed and checked parameters
       :param session_id: already validated session id of the user
    """
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    # read parameters
    polygons = parameters['polygons']

    new_images = []
    for file in images:
        t = triangler.Triangler(
            sample_method=triangler.SampleMethod.THRESHOLD, points=250)
        img = imread(os.path.join(image_path, file))
        img_tri = t.convert(img)
        new_images.append(img_tri)

    orderly_clear_images(session_id)
    for img in new_images:
        plt.imsave(os.path.join(image_path, file), new_images)

