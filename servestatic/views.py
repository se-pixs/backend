from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError


# Create your views here.
import os.path as path
import logging
import mimetypes


def static_icon(request, icon_name):
    try:
        icon_path = path.join(settings.ICONS_PATH, icon_name)
        icon = open(icon_path)

        content_type, encoding = mimetypes.guess_type(icon_path)
        if content_type is None:
            content_type = 'image/svg+xml'

        return HttpResponse(icon.read(), content_type=content_type)
    except FileNotFoundError:
        logging.error("Icon not found: %s" % icon_name)
        return HttpResponseServerError("Icon not found: %s" % icon_name)
