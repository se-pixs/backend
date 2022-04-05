from django.conf import settings
from django.http import HttpResponse
import json
import os


def open_json(filepath):
    with open(filepath, 'r') as f:
        return json.loads(f.read())


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


def build_image_root_by_id(session_id):
    return os.path.join(settings.IMAGES_ROOT, session_id)


def validate_request_session(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        return True
    else:
        return False
