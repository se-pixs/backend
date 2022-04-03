import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.conf import settings

import os
import json
from utils.fileSystem import *
from utils.miscellaneous import open_json, validate_request_session


@csrf_exempt
def index(request):
    if validate_request_session(request):
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            if handle_uploaded_file(request.FILES['file'], request.POST.get('format'), session_id):
                return HttpResponseRedirect('/')
            else:
                return HttpResponseServerError('Format not supported')  # TODO add error page
        else:
            form = UploadFileForm()
            return render(request, 'form.html', {'form': form})
            return HttpResponse("Hello from upload get")
    else:
        return HttpResponseServerError('Session not valid')  # TODO appropriate error handling


def handle_uploaded_file(f, format, session_id):
    create_image_dir(session_id)

    # open upload config
    try:
        upload_json = open_json(settings.ACTIONS_PATH)
    except IOError:
        logging.error("Could not open upload config")
        return False

    if format in upload_json['actions'][0]['format']['enum']:
        save_image(f, format.lower(), session_id)
        return True
    else:
        logging.error('Format not supported')
        return False
