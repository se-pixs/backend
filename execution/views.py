import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import ChangeFormatForm, ConvertToLowPolyForm, IGPanoSplitForm, GeneralForm

import triangler
from skimage.io import imread
import matplotlib.pyplot as plt
import os
from PIL import Image
from utils.parameterParser import parseParameters
import json
import math
import action_scripts as actions

from utils.miscellaneous import validate_request_session


def index(request):
    if validate_request_session(request):
        return HttpResponse("No action selected")
    else:
        return HttpResponseServerError('Session not valid')


@csrf_exempt
def execute(request, action_name):
    if validate_request_session(request):
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            try:
                parameters = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return HttpResponseServerError("Parameters not valid json")

            # dynamic calling of the script
            action_script_method = getattr(actions, action_name)
            action_result = action_script_method()
            # TODO http response
        else:
            form = GeneralForm()
            return render(request, 'form.html', {'form': form})
    else:
        return HttpResponseServerError('Session not valid')


@csrf_exempt
def ig_pano_split(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            try:
                parameters = json.loads(request.body.decode('utf-8'))
                parseParameters(parameters)
                return execute_ig_pano_split(parameters, session_id)
            except json.JSONDecodeError:
                return HttpResponseServerError("Parameters not valid")
        else:
            form = IGPanoSplitForm()
            return render(request, 'form.html', {'form': form})
    else:
        # TODO appropriate error handling
        return HttpResponseServerError('Session not valid')


def execute_ig_pano_split(parameters, session_id):
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)
    # open action configuration
    try:
        action_path = os.path.join(
            settings.CUSTOM_ACTIONS_PATH, 'igPanoSplit.json')
        action_config_json = json.loads(open(action_path).read())
    except IOError:
        logging.error("Could not open action configuration")
        return HttpResponseServerError("Action configuration not found for: " + action_path)
    except json.JSONDecodeError:
        logging.error("Action configuration is not valid JSON")
        return HttpResponseServerError("Action configuration is not valid JSON")

    # check if parameters are valid
    # ? is this necessary?
    max_width = next(x for x in filter(
        lambda x: x['name'] == 'max_width', parameters['parameters']['valuefields']))['value']
    max_height = next(x for x in filter(
        lambda x: x['name'] == 'max_height', parameters['parameters']['valuefields']))['value']
    min_allowed_width = next(x for x in filter(
        lambda x: x['name'] == 'max_width', action_config_json['parameters']['valuefields']))['value']['range'][0]
    max_allowed_width = next(x for x in filter(
        lambda x: x['name'] == 'max_width', action_config_json['parameters']['valuefields']))['value']['range'][1]
    min_allowed_height = next(x for x in filter(
        lambda x: x['name'] == 'max_height', action_config_json['parameters']['valuefields']))['value']['range'][0]
    max_allowed_height = next(x for x in filter(
        lambda x: x['name'] == 'max_height', action_config_json['parameters']['valuefields']))['value']['range'][1]
    if max_width < min_allowed_width or max_width > max_allowed_width:
        logging.error("Image width is not valid")
        return HttpResponseServerError("Image width is not valid. Got image width: " + str(max_width))
    if max_height < min_allowed_height or max_height > max_allowed_height:
        logging.error("Image height is not valid")
        return HttpResponseServerError("Image height is not valid. Got image height: " + str(max_height))

    # ? Are there any parameters  that are missing in the action configuration?
    if os.path.exists(image_path):
        file_count = len([name for name in os.listdir(image_path) if
                          os.path.isfile(os.path.join(image_path, name))])
        print(file_count)
        # ? Consider only processing the first/newest image to prevent overload?
        # ! Amount of images to process grows exponenentially if action performed repeatedly

        if file_count > 0:
            images_found = os.listdir(image_path)
            for file in images_found:
                if os.path.isfile(os.path.join(image_path, file)):
                    try:
                        # read image
                        image = Image.open(os.path.join(image_path, file))
                        width, height = image.size
                        # split image
                        print("shape:" + str(image.size))
                        if height > max_height:
                            # crop image to max_height
                            image = image.crop(
                                (0, int(height / 2 - (max_height / 2)), width, int(height / 2 + (max_height / 2))))
                            image.save(os.path.join(image_path, file), "JPEG")
                        if width > max_width:
                            # crop image to max_width
                            amount_of_splits = int(width / max_width)
                            for i in range(amount_of_splits):
                                tempImage = image.crop(
                                    (int(i * max_width), 0, int((i + 1) * max_width), height))
                                tempImage.save(os.path.join(
                                    image_path, "upload_" + str(i) + ".jpg"), "JPEG")
                    except FileNotFoundError as e:
                        logging.error("File not found: " +
                                      os.path.join(image_path, file))
                        return HttpResponseServerError("File not found: " + os.path.join(image_path, file))
                    except OSError as e:
                        print(format(e))
                        # TODO proper error handling
                        logging.error("Error while handling image")
                        return HttpResponseServerError("Error while handling image")
        else:
            return HttpResponseServerError("No files found")
    else:
        return HttpResponseServerError("No image uploaded")
    return HttpResponseRedirect('/')
