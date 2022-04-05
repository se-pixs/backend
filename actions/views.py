from django.shortcuts import render
import sys
import os
from os.path import normpath, join
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# custom imports
import uuid
import logging
import json
from utils.actionAssembler import assemble_actions, assemble_init_actions
from utils.fileSystem import check_image_exists

# add modules to path
sys.path.append(normpath(join(os.getcwd(), 'configurations')))


# Create your views here.
@csrf_exempt
def index(request):
    # check if session id exists # TODO check if session id is a valid one
    if 'session_id' in request.session:
        session_id = request.session['session_id']
    else:
        # set session id
        logging.info('Session ID not found, creating new session ID')
        # make uuid serializable because django bug
        session_id = uuid.uuid4().hex
        request.session['session_id'] = session_id

    # check if image exists
    if not check_image_exists(session_id):
        action_json = assemble_init_actions()
    else:
        # send initial action json
        action_json = assemble_actions(session_id)

    if action_json is None:
        # Error while assembling actions; see server logs for more info
        return HttpResponseServerError("An error occurred while providing the possible actions")
    else:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        response = HttpResponse(json.dumps(action_json), content_type='application/json')
        return response
