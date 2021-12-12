import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.conf import settings

import os
import json


@csrf_exempt
def index(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            if handle_uploaded_file(request.FILES['file'], request.POST['format'], session_id):
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
    else:
        # clear directory
        try:
            for file in os.listdir(os.path.join(settings.IMAGES_ROOT, session_id)):
                file_path = os.path.join(settings.IMAGES_ROOT, session_id, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            logging.error(e)
            return False

    # open upload config
    try:
        upload = open(settings.ACTIONS_PATH)
        upload_json = json.loads(upload.read())
    except IOError:
        logging.error("Could not open upload config")
        return False

    if format in upload_json['actions'][0]['format']['enum']:
        files = os.listdir(os.path.join(settings.IMAGES_ROOT, session_id))
        for file in files:
            if os.path.isfile(os.path.join(settings.IMAGES_ROOT, session_id, file)):
                os.remove(os.path.join(settings.IMAGES_ROOT, session_id, file))

        # TODO clear old files
        with open(os.path.join(settings.IMAGES_ROOT, session_id, 'upload.' + format.lower()), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return True
    else:
        logging.error('Format not supported')
        return False
