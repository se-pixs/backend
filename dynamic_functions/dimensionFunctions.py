from utils.miscellaneous import build_image_root_by_id
from utils.fileSystem import get_from_image_root
from PIL import Image
import os


def maxImageHeight(session_id):
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    maxHeight = -1
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        if image.height > maxHeight:
            maxHeight = image.height

    return maxHeight


def minImageHeight(session_id):
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    minHeight = 99999
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        if image.height < minHeight:
            minHeight = image.height

    return minHeight


def maxImageWidth(session_id):
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    maxWidth = -1
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        if image.width > maxWidth:
            maxWidth = image.width

    return maxWidth


def minImageWidth(session_id):
    image_path = build_image_root_by_id(session_id)
    images = get_from_image_root(session_id)

    minWidth = 99999
    for file in images:
        image = Image.open(os.path.join(image_path, file))
        if image.width < minWidth:
            minWidth = image.width

    return minWidth

