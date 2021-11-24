import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
import os
import mimetypes

# TODO : Improve logging and error handling


def download(request):
    if 'session_id' in request.session:
        session_id = request.session['session_id']
        if request.method == 'GET':
            image_path = os.path.join(settings.IMAGES_ROOT, session_id)
            if os.path.exists(image_path):
                file_count = len([name for name in os.listdir(image_path) if
                                  os.path.isfile(os.path.join(image_path, name))])
                if file_count > 0:
                    if file_count > 1:
                        # download as zip file
                        pass
                    else:
                        # download image
                        image_path = os.path.join(image_path, os.listdir(image_path)[0])
                        image = open(image_path, 'rb')
                        content_type, encoding = mimetypes.guess_type(image_path)
                        if content_type is None:
                            content_type = "image/" + image_path.split('.')[-1]
                        response = HttpResponse(image, content_type=content_type)
                        return response
                else:
                    # no images
                    logging.ERROR('No images found for session_id: ' + session_id)
                    return HttpResponse("No images to download found")

            else:
                # no images
                logging.ERROR("No directory for session id: " + session_id)
                return HttpResponse("No images found with session id")
    else:
        logging.WARNING("No session id found")
        return HttpResponseServerError('Session invalid')
