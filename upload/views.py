import logging

from django.shortcuts import render
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.conf import settings

import os
from utils.fileSystem import *
from utils.miscellaneous import open_json, validate_request_session


@csrf_exempt
def index(request):
    if validate_request_session(request):
        session_id = request.session['session_id']
        if request.method == 'POST':
            if handle_uploaded_file(request.FILES['image'], request.POST.get('format'), session_id):
                return HttpResponseRedirect('/')
            else:
                return HttpResponseServerError('Format not supported')  # TODO add error page
        else:
            form = UploadFileForm()
            return render(request, 'form.html', {'form': form})
    else:
        return HttpResponseServerError('Session not valid')  # TODO appropriate error handling


def handle_uploaded_file(f, format, session_id):
    create_image_dir(session_id)

    # open upload config
    try:
        upload_json = open_json(os.path.join(settings.BASE_ACTIONS_PATH, 'upload.json'))
    except IOError:
        logging.error("Could not open upload config")
        return False

    if format in upload_json['format']['enum']:
        save_image(f, format.lower(), session_id)
        return True
    else:
        logging.error('Format not supported')
        return False
