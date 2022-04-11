import sys
import os
from os.path import normpath, join
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# custom imports
import logging
import json
from utils.miscellaneous import generate_session_id, validate_request_session
from utils.actionAssembler import assemble_actions


# add modules to path
sys.path.append(normpath(join(os.getcwd(), 'configurations')))


# Create your views here.
@csrf_exempt
def index(request):
    # check if session id exists
    if validate_request_session(request):
        session_id = request.session['session_id']
    else:
        # set session id
        logging.info('Session ID not found, creating new session ID')
        session_id = generate_session_id()
        request.session['session_id'] = session_id

    action_json = assemble_actions(session_id)

    if action_json is None:
        # Error while assembling actions; see server logs for more info
        return HttpResponseServerError("An error occurred while providing the possible actions")
    else:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        response = HttpResponse(json.dumps(action_json), content_type='application/json')
        return response
