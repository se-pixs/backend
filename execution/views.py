import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.conf import settings
from .forms import ChangeFormatForm

import os
from PIL import Image
import json


def index(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        return HttpResponse("No action selected")
    else:
        return HttpResponse("Session not valid")


def change_format(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            form = ChangeFormatForm(request.POST, request.FILES)
            if form.is_valid():
                return execute_change_format(request.FILES['parameters'], session_id)
            else:
                return HttpResponseServerError("Form is not valid")
        else:
            form = ChangeFormatForm()
            return render(request, 'form.html', {'form': form})
    else:
        return HttpResponseServerError('Session not valid')  # TODO appropriate error handling

    return HttpResponse("changeFormat")


def execute_change_format(parameters, session_id):
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)
    try:
        parameters_json = json.loads(parameters.read())
    except json.JSONDecodeError:
        logging.error("Parameters are not valid JSON")
        return HttpResponseServerError("Parameters are not valid JSON")

    # open action configuration
    try:
        action_path = os.path.join(settings.CUSTOM_ACTIONS_PATH, 'changeFormat.json')
        action_config_json = json.loads(open(action_path).read())
    except IOError:
        logging.error("Could not open action configuration")
        return HttpResponseServerError("Action configuration not found for: " + action_path)
    except json.JSONDecodeError:
        logging.error("Action configuration is not valid JSON")
        return HttpResponseServerError("Action configuration is not valid JSON")

    # TODO dynamic parsing to dictionarys for easier access of the parameters
    # TODO include code for setting the fill color for PNG to JPEG conversion
    convert_format = parameters_json['parameters']['valuefields'][0]['value']
    fill_color = parameters_json['parameters']['colorpickers'][0]['input']['red'], \
                 parameters_json['parameters']['colorpickers'][0]['input']['green'], \
                 parameters_json['parameters']['colorpickers'][0]['input']['blue']

    if convert_format not in action_config_json['parameters']['valuefields'][0]['value']['range']:
        logging.error("Format not allowed")
        return HttpResponseServerError("Format not in range")

    if os.path.exists(image_path):
        file_count = len([name for name in os.listdir(image_path) if
                          os.path.isfile(os.path.join(image_path, name))])
        if file_count > 0:
            images_found = os.listdir(image_path)
            for file in images_found:
                if os.path.isfile(os.path.join(image_path, file)):
                    try:
                        image = Image.open(os.path.join(image_path, file))
                        image_name = file.split('.')[0] + '.' + convert_format
                        if convert_format == 'JPEG':
                            image = image.convert("RGBA")
                            if image.mode in ('RGBA', 'LA'):
                                im_background = Image.new(image.mode[:-1], image.size, fill_color)
                                im_background.paste(image, image.split()[-1])
                                image = im_background
                            image.convert("RGB").save(os.path.join(image_path, image_name), "JPEG")
                        elif convert_format == 'PNG':
                            image.convert("RGBA").save(os.path.join(image_path, image_name), "PNG")
                        else:
                            logging.error("Format not allowed")
                            return HttpResponseServerError("Format not allowed")
                        if file != image_name:
                            os.remove(os.path.join(image_path, file))
                    except FileNotFoundError:
                        logging.error("File not found: " + os.path.join(image_path, file))
                        return HttpResponseServerError("File not found")
                    except OSError as e:
                        print(format(e))
                        # TODO proper error handling
                        logging.error("Error while handling image")
                        return HttpResponseServerError("Error while handling image")
        else:
            return HttpResponseServerError("No files found")
    return HttpResponseRedirect('/')
