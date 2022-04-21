# default imports for loading and saving images
from skimage.io import imread
from utils.fileSystem import get_from_image_root, save_pillow_images

# action specific imports
from pyxelate import Pyx


def convertToPixelArt(parameters, session_id):
    # TODO error handling
    """
       :param parameters: already parsed and checked parameters
       :param session_id: already validated session id of the user
    """
    images = get_from_image_root(session_id)
    image_format = images[0].split('.')[-1]

    # read parameters
    factor = parameters['downsample_factor']
    palette = parameters['color_palette']

    new_images = []
    for file in images:
        pyx = Pyx(factor=factor, palette=palette)
        img = imread(file)
        pyx.fit(img)
        img_pixel_art = pyx.transform(img)
        new_images.append(img_pixel_art)

    save_pillow_images(new_images, image_format, session_id, use_imsave=True)

    return 0
