import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, FileResponse
from django.conf import settings
import os
import mimetypes
from zipfile import ZipFile
from utils.miscellaneous import validate_request_session
from utils.fileSystem import check_image_destination, extract_image_dir

# TODO : Improve logging and error handling


def download(request):
    if validate_request_session(request):
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'GET':
            return extract_image_dir(session_id)
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')


def preview(request):
    if validate_request_session(request):
        pass # TODO : Implement
