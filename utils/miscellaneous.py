from django.conf import settings
import json
from uuid import UUID, uuid4
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
    # TODO Keep track of used session ids and check if current session id is valid
    if 'session_id' in request.session:
        try:
            UUID(request.session['session_id'])
            request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
            return True
        except ValueError:
            return False
    else:
        return False

def generate_session_id():
    # make uuid serializable because django bug
    return uuid4().hex