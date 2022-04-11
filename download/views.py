import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, FileResponse
from django.conf import settings
from utils.miscellaneous import validate_request_session
from utils.fileSystem import extract_image_dir

# TODO : Improve logging and error handling


def download(request):
    if validate_request_session(request):
        session_id = request.session['session_id']
        if request.method == 'GET':
            return extract_image_dir(session_id)
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')


def preview(request):
    if validate_request_session(request):
        pass # TODO : Implement
