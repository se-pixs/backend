from django.conf import settings
import os
import shutil


def create_image_dir(session_id):
    """
    Create image directory for session id
    """
    try:
        if not os.path.exists(os.path.join(settings.IMAGES_ROOT, session_id)):
            os.makedirs(os.path.join(settings.IMAGES_ROOT, session_id))
    except OSError:
        print("Error creating image directory with path: " + os.path.join(settings.IMAGES_ROOT, session_id))


def create_image_reverse_dir(session_id):
    try:
        if not os.path.exists(os.path.join(settings.IMAGES_ROOT, session_id, 'reverse')):
            os.makedirs(os.path.join(settings.IMAGES_ROOT, session_id, 'reverse'))
    except OSError:
        print("Error creating reverse image directory with path: " + os.path.join(settings.IMAGES_ROOT, session_id,
                                                                                  'reverse'))


def orderly_clear_images(session_id):
    """
    Clear images from current state to reverse dir
    """
    if os.path.exists(os.path.join(settings.IMAGES_ROOT, session_id, 'reverse')):
        # clear reverse dir if it is not empty
        shutil.rmtree(os.path.join(settings.IMAGES_ROOT, session_id, 'reverse'))

    create_image_reverse_dir(session_id)
    image_root_path = os.path.join(settings.IMAGES_ROOT, session_id)
    for f in os.listdir(os.path.join(image_root_path)):
        if os.path.isfile(os.path.join(image_root_path, f)):
            shutil.move(os.path.join(image_root_path, f), os.path.join(settings.IMAGES_ROOT, session_id, 'reverse', f))


def save_file(file, name, session_id):
    """
    Save image to disk
    """
    create_image_dir(session_id)
    with open(os.path.join(settings.IMAGES_ROOT, session_id, name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def save_image(image, image_format, session_id):
    save_file(image, 'upload.' + image_format.lower(), session_id)


def save_images(images, image_format, session_id):
    for index, image in enumerate(images):
        save_file(image, 'upload{}.'.format(index + 1) + image_format.lower(), session_id)
