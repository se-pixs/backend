from django.shortcuts import render
import sys
import os
from os.path import normpath, join
from django.http import HttpResponse, HttpResponseServerError

# add modules to path
sys.path.append(normpath(join(os.getcwd(), 'configurations')))

# custom imports
import uuid
import logging
import server
import json


# Create your views here.
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
        request.session.set_expiry(server.SESSION_EXPIRATION_TIME)
        return HttpResponse(json.dumps(action_json), content_type='application/json')

# TODO : export to json methods to separate file


def assemble_actions():
    wd = os.getcwd()
    try:
        actions = open(normpath(join(wd, server.ACTIONS_PATH)))
        actions_json = json.loads(actions.read())

        # insert all custom actions into actions
        for action in actions_json['customActions']:
            actions_json['actions'].append(insert_custom_action(action, actions_json))

        # remove custom actions
        if 'customActions' in actions_json:
            del actions_json['customActions']

        # clean up
        actions.close()
        return actions_json
    except IOError:
        # clean up
        actions.close()
        logging.error('Could not open actions file with path: ' + server.ACTIONS_PATH)
        return None


def insert_custom_action(custom_action_name, actions_json):
    # check if custom action exists
    wd = os.getcwd()
    try:
        custom_action_path = normpath(join(wd, server.CUSTOM_ACTIONS_PATH, custom_action_name + '.json'))
        custom_action = open(custom_action_path)

        custom_action_json = json.loads(custom_action.read())

        # replace paramters in custom action with input json
        custom_action_json = insert_inputs(custom_action_json)

        # clean up
        custom_action.close()
        return custom_action_json

    except (IOError, json.decoder.JSONDecodeError):  # TODO error message
        logging.error('Could not open custom actions file with path: ' + custom_action_path)
        # clean up
        custom_action.close()
        return None


def insert_inputs(custom_action_json):
    wd = os.getcwd()

    # create result json
    result_json = {}
    # insert static parameters TODO : make this dynamic
    result_json.update({'name': custom_action_json['name']})
    result_json.update({'description': custom_action_json['description']})
    result_json.update({'helpMessage': custom_action_json['helpMessage']})
    result_json.update({'path': custom_action_json['path']})
    result_json.update({'parameters': {}})

    # get possible inputs for validation
    possible_inputs = open(normpath(join(wd, server.POSSIBLE_INPUTS_PATH)))
    possible_inputs_json = json.loads(possible_inputs.read())

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
    input_json = {}

    # insert static parameters TODO : make this dynamic
    input_json.update({'name': custom_input['name']})
    input_json.update({'description': custom_input['description']})
    input_json.update({'type': custom_input['type']})
    input_json.update({'range': custom_input['range']})
    input_json.update({'default': custom_input['default']})

    return input_json


def replace_colorpicker_input(custom_input):
    input_json = {}

    # insert static parameters TODO : make this dynamic
    input_json.update({'name': custom_input['name']})
    input_json.update({'description': custom_input['description']})

    rgb = hex_to_rgb(custom_input['input']['default'])
    input_json.update({'input': {'red': { "minimum": 0, "maximum": 255, "default": rgb[0]},
                                 'green': { "minimum": 0, "maximum": 255, "default": rgb[1]} ,
                                 'blue': { "minimum": 0, "maximum": 255, "default": rgb[2] }}})

    return input_json


def replace_slider_input(custom_input):
    input_json = {}

    # insert static parameters TODO : make this dynamic
    input_json.update({'name': custom_input['name']})
    input_json.update({'description': custom_input['description']})
    input_json.update({'value': 1})
    input_json.update({'minimum': custom_input['minimum']})
    input_json.update({'maximum': custom_input['maximum']})
    input_json.update({'default': custom_input['default']})

    return input_json


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))