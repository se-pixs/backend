from django.shortcuts import render
import sys
import os
from os.path import normpath, join
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# add modules to path
sys.path.append(normpath(join(os.getcwd(), 'configurations')))

# custom imports
import uuid
import logging
import json
from xml.dom import minidom


# Create your views here.
@csrf_exempt
def index(request):
    # check if session id exists
    if 'session_id' in request.session:
        session_id = request.session['session_id']
        # check if an image exists
    else:
        # set session id
        logging.info('Session ID not found, creating new session ID')
        # make uuid serializable because django bug
        request.session['session_id'] = uuid.uuid4().hex

    # send initial action json
    action_json = assemble_actions()
    if action_json is None:
        # Error while assembling actions; see server logs for more info
        return HttpResponseServerError("An error occurred while providing the possible actions")
    else:
        request.session.set_expiry(settings.SESSION_EXPIRATION_TIME)
        response = HttpResponse(json.dumps(action_json), content_type='application/json')
        return response


# TODO : export to json methods to separate file


def assemble_actions():
    try:
        actions = open(settings.ACTIONS_PATH)
        actions_json = json.loads(actions.read())

        # insert all custom actions into actions
        for action in actions_json['customActions']:
            actions_json['actions'].append(insert_custom_action(action))

        # remove custom actions
        if 'customActions' in actions_json:
            del actions_json['customActions']

        # clean up
        actions.close()

        actions_json = replace_icons(actions_json)

        return actions_json
    except IOError:
        # clean up
        actions.close()
        logging.error('Could not open actions file with path: ' + settings.ACTIONS_PATH)
        return None


def replace_icons(actions_json):
    for action in actions_json['actions']:
        if 'icon' in action:
            if action['icon'] != "":
                # replace icon with corresponding svg tag
                icon_path = '/servestatic/' + 'icon/' + action['icon']
                action.update({'icon': icon_path})

    return actions_json


def insert_custom_action(custom_action_name):
    # check if custom action exists
    try:
        custom_action_path = join(settings.CUSTOM_ACTIONS_PATH, custom_action_name + '.json')
        custom_action = open(custom_action_path)

        custom_action_json = json.loads(custom_action.read())

        # replace parameters in custom action with input json
        custom_action_json.update(insert_inputs(custom_action_json))

        # clean up
        custom_action.close()
        return custom_action_json

    except IOError:
        logging.error('Could not open custom actions file with path: ' + custom_action_path)
        # clean up
        custom_action.close()
        return None
    except json.decoder.JSONDecodeError:
        logging.error('Could not decode custom actions file with path: ' + custom_action_path)
        # clean up
        custom_action.close()
        return None


def insert_inputs(custom_action_json):
    # create result json
    result_json = {'parameters': {}}

    try:
        # get possible inputs for validation
        possible_inputs = open(settings.POSSIBLE_INPUTS_PATH)
        possible_inputs_json = json.loads(possible_inputs.read())
    except IOError:
        logging.error('Could not open possible inputs file with path: ' + settings.POSSIBLE_INPUTS_PATH)
        # clean up
        possible_inputs.close()
        return None

    # add all defined inputs to result json
    for input in possible_inputs_json['inputs']:
        result_json['parameters'].update({input: []})
        if input in custom_action_json['parameters']:
            for custom_input in custom_action_json['parameters'][input]:
                if input == 'valuefields':
                    result_json['parameters'][input].append(replace_valuefield_input(custom_input))
                elif input == 'colorpickers':
                    result_json['parameters'][input].append(replace_colorpicker_input(custom_input))
                elif input == 'sliders':
                    result_json['parameters'][input].append(replace_slider_input(custom_input))
                else:
                    logging.error('Input type not supported: ' + input)
                    # clean up
                    possible_inputs.close()
                    return None

    # clean up
    possible_inputs.close()

    return result_json


def replace_valuefield_input(custom_input):
    try:
        default_valuefield = open(join(settings.INPUTS_PATH, 'valuefield.json'))
        default_valuefield_json = json.loads(default_valuefield.read())
    except IOError:
        logging.error('Could not open valuefield.json')
        # clean up
        default_valuefield.close()
        return None

    # insert static parameters TODO : make this dynamic
    default_valuefield_json.update({'name': custom_input['name']})
    default_valuefield_json.update({'description': custom_input['description']})

    # build value json
    value_json = {}
    if custom_input['value']['type'] in default_valuefield_json['value']['type']:
        value_json.update({'type': custom_input['value']['type']})
        value_json.update({'range': custom_input['value']['range']})
        value_json.update({'default': custom_input['value']['default']})
    else:
        logging.error('Value type not supported: ' + custom_input['value']['type'])
        # clean up
        default_valuefield.close()
        return None

    # insert value json
    default_valuefield_json.update({'value': value_json})

    # clean up
    default_valuefield.close()

    return default_valuefield_json


def replace_colorpicker_input(custom_input):
    input_json = {}

    # insert static parameters TODO : make this dynamic
    input_json.update({'name': custom_input['name']})
    input_json.update({'description': custom_input['description']})

    rgb = hex_to_rgb(custom_input['default'])
    input_json.update({'input': {'red': {"minimum": 0, "maximum": 255, "default": rgb[0]},
                                 'green': {"minimum": 0, "maximum": 255, "default": rgb[1]},
                                 'blue': {"minimum": 0, "maximum": 255, "default": rgb[2]}}})

    return input_json


def replace_slider_input(custom_input):
    try:
        default_slider = open(join(settings.INPUTS_PATH, 'slider.json'))
        default_slider_json = json.loads(default_slider.read())
    except IOError:
        logging.error('Could not open slider.json')
        # clean up
        default_slider.close()
        return None

    # insert static parameters TODO : make this dynamic
    default_slider_json.update({'name': custom_input['name']})
    default_slider_json.update({'description': custom_input['description']})

    value_json = {}
    value_json.update({'min': custom_input['value']['min']})
    value_json.update({'max': custom_input['value']['max']})
    value_json.update({'step': custom_input['value']['step']})
    value_json.update({'default': custom_input['value']['default']})

    default_slider_json.update({'value': value_json})

    # clean up
    default_slider.close()

    return default_slider_json


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
