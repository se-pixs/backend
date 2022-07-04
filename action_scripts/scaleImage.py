# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
from PIL import Image
from action_scripts.action import Action


class CustomAction(Action):

    @staticmethod
    def scaleImage(parameters, session_id):
        """
        :param parameters: already parsed and checked parameters
        :param session_id: already validated session id of the user
        """
        images = get_from_image_root(session_id)
        status = ExecutionStatus()

        # read parameters
        width = parameters['width']
        new_images = []
        for file in images:
            image_format = file.split('.')[-1]
            image = Image.open(file)
            im_width, im_height = image.size
            # maintain aspect ratio
            new_width = width
            new_height = int(im_height * (new_width / im_width))
            try:
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
                new_images.append(image)
            except Exception as e:
                status.set_status("Error: Image could not be scaled")
                return status
        save_pillow_images(new_images, image_format, session_id)
        status.set_status(Status.SUCCESS)
        return status
