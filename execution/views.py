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
        else:
            form = GeneralForm()
            return render(request, 'form.html', {'form': form})
    else:
        return HttpResponseServerError('Session not valid')


@csrf_exempt
def change_format(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            try:
                parameters = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return HttpResponseServerError("Parameters not valid")
            return execute_change_format(parameters, session_id)
        else:
            form = ChangeFormatForm()
            return render(request, 'form.html', {'form': form})
    else:
        # TODO appropriate error handling
        return HttpResponseServerError('Session not valid')


@csrf_exempt
def convert_to_low_poly(request):
    if 'session_id' in request.session:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        session_id = request.session['session_id']
        if request.method == 'POST':
            try:
                parameters = json.loads(request.body.decode('utf-8'))
                return execute_change_to_low_poly(parameters, session_id)
            except json.JSONDecodeError:
                return HttpResponseServerError("Parameters not valid")
        else:
            form = ConvertToLowPolyForm()
            return render(request, 'form.html', {'form': form})
    else:
        # TODO appropriate error handling
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


def execute_change_to_low_poly(parameters, session_id):
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)

    # open action configuration
    try:
        action_path = os.path.join(
            settings.CUSTOM_ACTIONS_PATH, 'convertToLowPoly.json')
        action_config_json = json.loads(open(action_path).read())
    except IOError:
        logging.error("Could not open action configuration")
        return HttpResponseServerError("Action configuration not found for: " + action_path)
    except json.JSONDecodeError:
        logging.error("Action configuration is not valid JSON")
        return HttpResponseServerError("Action configuration is not valid JSON")
    polygons = parameters['parameters']['sliders'][0]['value']
    if polygons > action_config_json['parameters']['sliders'][0]['value']['max'] or polygons < \
            action_config_json['parameters']['sliders'][0]['value']['min']:
        logging.error("Amount of Polygon not allowed")
        return HttpResponseServerError("Polygons not in range of allowed values")
    if os.path.exists(image_path):
        file_count = len([name for name in os.listdir(image_path) if
                          os.path.isfile(os.path.join(image_path, name))])
        if file_count > 0:
            images_found = os.listdir(image_path)
            for file in images_found:
                if os.path.isfile(os.path.join(image_path, file)):
                    try:
                        t = triangler.Triangler(
                            sample_method=triangler.SampleMethod.THRESHOLD, points=250)
                        img = imread(os.path.join(image_path, file))
                        img_tri = t.convert(img)
                        plt.imsave(os.path.join(image_path, file), img_tri)
                    except FileNotFoundError:
                        logging.error("File not found: " +
                                      os.path.join(image_path, file))
                        return HttpResponseServerError("File not found")
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


def execute_change_format(parameters, session_id):
    image_path = os.path.join(settings.IMAGES_ROOT, session_id)
    # open action configuration
    try:
        action_path = os.path.join(
            settings.CUSTOM_ACTIONS_PATH, 'changeFormat.json')
        action_config_json = json.loads(open(action_path).read())
    except IOError:
        logging.error("Could not open action configuration")
        return HttpResponseServerError("Action configuration not found for: " + action_path)
    except json.JSONDecodeError:
        logging.error("Action configuration is not valid JSON")
        return HttpResponseServerError("Action configuration is not valid JSON")

    # TODO dynamic parsing to dictionarys for easier access of the parameters
    # TODO include code for setting the fill color for PNG to JPEG conversion
    convert_format = parameters['parameters']['valuefields'][0]['value']
    fill_color = parameters['parameters']['colorpickers'][0]['input']['red'], \
                 parameters['parameters']['colorpickers'][0]['input']['green'], \
                 parameters['parameters']['colorpickers'][0]['input']['blue']

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
                            image.convert("RGBA").save(
                                os.path.join(image_path, image_name), "PNG")
                        else:
                            logging.error("Format not allowed")
                            return HttpResponseServerError("Format not allowed")
                        if file != image_name:
                            os.remove(os.path.join(image_path, file))
                    except FileNotFoundError:
                        logging.error("File not found: " +
                                      os.path.join(image_path, file))
                        return HttpResponseServerError("File not found")
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
