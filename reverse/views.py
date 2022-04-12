import logging

from django.conf import settings
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from utils.miscellaneous import validate_request_session
import os
import shutil


@csrf_exempt
def index(request):
    if validate_request_session(request):
        session_id = request.session['session_id']
        if request.method == 'GET':
            restore_previous_state(session_id)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseServerError('Method not allowed')
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')


def restore_previous_state(session_id):
    """
    Restore previous state of images
    """
    reverse_dir = os.path.join(settings.IMAGES_ROOT, session_id, settings.REVERSE_STACK_PATH)
    session_dir = os.path.join(settings.IMAGES_ROOT, session_id)
    if os.path.exists(reverse_dir):
        dirs = [name for name in os.listdir(reverse_dir) if os.path.isdir(os.path.join(reverse_dir, name))]
        # check if reverse is possible
        if not os.listdir(os.path.join(reverse_dir, dirs[0])):
            return

        # remove all files in session dir
        for file in [name for name in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, name))]:
            os.remove(os.path.join(session_dir, file))

        # move all files of latest reverse stack dir to session dir
        for f in os.listdir(os.path.join(reverse_dir, dirs[0])):
            if os.path.isfile(os.path.join(reverse_dir, dirs[0], f)):
                shutil.move(os.path.join(reverse_dir, dirs[0], f), os.path.join(session_dir, f))

        # replace latest reverse stack dir with previous ones
        for index, dir in enumerate(dirs[1:]):
            shutil.rmtree(os.path.join(reverse_dir, dirs[index]))
            shutil.copytree(os.path.join(reverse_dir, dir),
                            os.path.join(reverse_dir, dirs[index]))
