# default imports for loading and saving images
from skimage.io import imread
from PIL import Image
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
from pyxelate import Pyx
from action_scripts.action import Action


class CustomAction(Action):

    @staticmethod
    def execute(parameters, session_id):
        """
        :param parameters: already parsed and checked parameters
        :param session_id: already validated session id of the user
        """
        images = get_from_image_root(session_id)
        image_format = images[0].split('.')[-1]
        status = ExecutionStatus()

        # read parameters
        factor = parameters['Downsample']
        palette = parameters['Colorpalette']

        new_images = []
        pyx = Pyx(factor=factor, palette=palette)
        for file in images:
            img = imread(file)
            pyx.fit(img)
            img_pixel_art = pyx.transform(img)
            # convert to PIL image
            new_images.append(Image.fromarray(img_pixel_art))

        save_pillow_images(new_images, image_format, session_id)

        status.set_status(Status.SUCCESS)
        return status
