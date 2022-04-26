import logging

from django.http import HttpResponseServerError
from utils.miscellaneous import validate_request_session
from utils.fileSystem import extract_image_dir


def download(request):
    if validate_request_session(request):
        session_id = request.session['session_id']
        if request.method == 'GET':
            try:
                http_response = extract_image_dir(session_id)
            except Exception as e:
                http_response = HttpResponseServerError("Error while packing the images")
            return http_response
        else:
            return HttpResponseServerError("Method not allowed for download")
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')


def preview(request):
    if validate_request_session(request):
        pass
