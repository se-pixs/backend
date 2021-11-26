import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from .forms import UploadFileForm
from django.conf import settings

import os
import json


def index(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                if handle_uploaded_file(request.FILES['image'], form.data['format'], session_id):
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
    if not os.path.exists(os.path.join(settings.IMAGES_ROOT, session_id)):
        os.makedirs(os.path.join(settings.IMAGES_ROOT, session_id))

    # open upload config
    try:
        upload = open(settings.ACTIONS_PATH)
        upload_json = json.loads(upload.read())
    except IOError:
        logging.error("Could not open upload config")
        return False

    if format in upload_json['actions'][0]['format']['enum']:
        with open(os.path.join(settings.IMAGES_ROOT, session_id, 'upload.' + format.lower()), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return True
    else:
        logging.error('Format not supported')
        return False
