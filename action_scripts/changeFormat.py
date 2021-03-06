# default imports for loading and saving images
from utils.fileSystem import get_from_image_root, save_pillow_images
from utils.executionStatus import ExecutionStatus, Status

# action specific imports
from action_scripts.action import Action
from PIL import Image


class CustomAction(Action):
    @staticmethod
    def execute(parameters, session_id):
        """
        :param parameters: already parsed and checked parameters
        :param session_id: already validated session id of the user
        """
        images = get_from_image_root(session_id)
        status = ExecutionStatus()

        # read parameters
        convert_format = parameters['format']
        fill_color = parameters['fillcolor']['red'],\
            parameters['fillcolor']['green'],\
            parameters['fillcolor']['blue']

        new_images = []
        for file in images:
            try:
                image = Image.open(file)
            except OSError:
                status.set_message(f"Could not read image {file}")
                status.set_status(Status.FAILURE)
                return status

            if convert_format == 'JPEG':
                image = image.convert("RGBA")
                if image.mode in ('RGBA', 'LA'):
                    im_background = Image.new(
                        image.mode[:-1], image.size, fill_color)
                    im_background.paste(image, image.split()[-1])
                    image = im_background
                new_images.append(image.convert("RGB"))
            elif convert_format == 'PNG':
                new_images.append(image.convert("RGBA"))

        save_pillow_images(new_images, convert_format, session_id)

        status.set_status(Status.SUCCESS)
        return status
    