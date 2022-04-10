import logging

from django.conf import settings
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt

from utils.miscellaneous import validate_request_session


@csrf_exempt
def index(request):
    if validate_request_session(request):
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'GET':
            return restore_previous_state(session_id)
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')


def restore_previous_state(session_id):
    pass
