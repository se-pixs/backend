from django.conf import settings
from django.http import HttpResponse, FileResponse, HttpResponseNotFound, HttpResponseServerError
from zipfile import ZipFile
import os
import mimetypes
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
        reverse_folder_path = os.path.join(settings.IMAGES_ROOT, session_id, settings.REVERSE_STACK_PATH)
        if not os.path.exists(os.path.join(reverse_folder_path)):
            os.makedirs(os.path.join(reverse_folder_path))
            for index in range(settings.MAX_REVERSE_STACK_SIZE):
                try:
                    os.makedirs(os.path.join(reverse_folder_path, 'state_' + str(index)))
                except OSError:
                    print("Error creating image reverse directory with path: " + os.path.join(reverse_folder_path,
                                                                                              'state_' + str(index)))
    except OSError:
        print("Error creating reverse image directory with path: " + os.path.join(reverse_folder_path))


def orderly_clear_images(session_id):
    """
    Clear images from current state to reverse dir
    """
    reverse_folder_path = os.path.join(settings.IMAGES_ROOT, session_id, settings.REVERSE_STACK_PATH)
    if os.path.exists(reverse_folder_path):
        dirs = [name for name in os.listdir(reverse_folder_path) if
                os.path.isdir(os.path.join(reverse_folder_path, name))]
        number_of_directories = settings.MAX_REVERSE_STACK_SIZE - 1
        for index in reversed(range(number_of_directories)):
            shutil.rmtree(os.path.join(reverse_folder_path, dirs[index + 1]))
            shutil.copytree(os.path.join(reverse_folder_path, dirs[index]),
                            os.path.join(reverse_folder_path, dirs[index + 1]))

    else:
        create_image_reverse_dir(session_id)

    image_root_path = os.path.join(settings.IMAGES_ROOT, session_id)
    for f in os.listdir(os.path.join(image_root_path)):
        if os.path.isfile(os.path.join(image_root_path, f)):
            shutil.move(os.path.join(image_root_path, f), os.path.join(reverse_folder_path, "state_0", f))


def save_file(file, name, session_id):
    """
    Save image to disk
    """
    create_image_dir(session_id)
    with open(os.path.join(settings.IMAGES_ROOT, session_id, name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def save_pillow_image(image, name, session_id):
    """
    Save pillow image to disk
    """
    create_image_dir(session_id)
    image.save(os.path.join(settings.IMAGES_ROOT, session_id, name))


def save_image(image, image_format, session_id):
    """
    Save uploaded image to disk
    """
    orderly_clear_images(session_id)
    save_file(image, 'upload.' + image_format.lower(), session_id)


def save_images(images, image_format, session_id):
    orderly_clear_images(session_id)
    for index, image in enumerate(images):
        save_file(image, 'upload{}.'.format(index + 1) + image_format.lower(), session_id)


def save_pillow_images(images, image_format, session_id):
    orderly_clear_images(session_id)
    for index, image in enumerate(images):
        save_pillow_image(image, 'upload{}.'.format(index + 1) + image_format.lower(), session_id)


def check_image_destination(session_id):
    """
    Check if image destination exists
    """
    if not os.path.exists(os.path.join(settings.IMAGES_ROOT, session_id)):
        return False
    return True


def check_image_exists(session_id):
    """
    Check if any images exist
    """
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)
    if os.path.exists(image_path):
        files = [name for name in os.listdir(image_path) if
                 os.path.isfile(os.path.join(image_path, name))]
        file_count = len(files)
        if file_count > 0:
            return True
    return False


def extract_image_dir(session_id):
    """
    Extract image directory to HTTP response
    """
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)
    if check_image_destination(session_id):
        files = [name for name in os.listdir(image_path) if
                 os.path.isfile(os.path.join(image_path, name))]
        file_count = len(files)
        if file_count > 0:
            if file_count > 1:
                # return as zip
                return FileResponse(extract_files_to_zip(image_path, files))
            else:
                # return as image
                image_path = os.path.join(image_path, files[0])
                return read_image_to_http_response(image_path)
        else:
            return HttpResponseNotFound("No images found")
    else:
        return HttpResponseServerError("Image directory does not exist")


def extract_files_to_zip(path, files):
    """
    Extract image directory to zip
    """
    with ZipFile(os.path.join(path, 'download.zip'), 'w') as zip_file:
        for file in files:
            zip.write(os.path.join(path, file))

        return zip_file


def read_image_to_http_response(image_path):
    with open(image_path, 'rb') as image:
        content_type, encoding = mimetypes.guess_type(image_path)
        if content_type is None:
            content_type = "image/" + image_path.split('.')[-1]
        return HttpResponse(image.read(), content_type=content_type)


# TODO error handling
def get_from_image_root(session_id):
    images = []
    if check_image_destination(session_id):
        image_path = os.path.join(settings.IMAGES_ROOT, session_id)
        files = [name for name in os.listdir(image_path) if
                 os.path.isfile(os.path.join(image_path, name))]
        file_count = len(files)
        if file_count > 0:
            for f in files:
                images.append(os.path.join(image_path, f))
        else:
            pass

    return images
