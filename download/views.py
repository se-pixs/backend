import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, FileResponse
from django.conf import settings
import os
import mimetypes
from zipfile import ZipFile

# TODO : Improve logging and error handling


def download(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'GET':
            image_path = os.path.join(settings.IMAGES_ROOT, session_id)
            if os.path.exists(image_path):
                file_count = len([name for name in os.listdir(image_path) if
                                  os.path.isfile(os.path.join(image_path, name))])
                if file_count > 0:
                    if file_count > 1:
                        # download as zip file
                        with ZipFile(os.path.join(image_path, 'download.zip'), 'w') as zip_file:
                            for file in os.listdir(image_path):
                                if os.path.isfile(os.path.join(image_path, file)) and file != 'download.zip':
                                    zip_file.write(os.path.join(image_path, file), arcname=file)

                        return FileResponse(open(os.path.join(image_path, 'download.zip'), 'rb'))

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
                    logging.error('No images found for session_id: ' + session_id)
                    return HttpResponse("No images to download found")

            else:
                # no images
                logging.error("No directory for session id: " + session_id)
                return HttpResponse("No images found with session id")
    else:
        logging.warning("No session id found")
        return HttpResponseServerError('Session invalid')
