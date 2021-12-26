from django.conf import settings
import json
from utils.miscellaneous import open_json
import os


# TODO add exeception handling
def assemble_actions():
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    try:
        actions_json = open_json(settings.ACTIONS_PATH)

        # insert all custom actions into actions
        for action in actions_json['customActions']:
            inserted_custom_action = insert_custom_action(action)
            if inserted_custom_action is None:
                action_logger.error('Could not insert custom action with name: ' + action)
                return None
            actions_json['actions'].append(inserted_custom_action)

        # remove custom actions
        if 'customActions' in actions_json:
            del actions_json['customActions']

        actions_json = replace_icons(actions_json)

        return actions_json
    except IOError:
        action_logger.error('Could not open actions file with path: ' + settings.ACTIONS_PATH)
        return None


def insert_custom_action(custom_action_name):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    # check if custom action exists
    try:
        custom_action_path = os.path.join(settings.CUSTOM_ACTIONS_PATH, custom_action_name + '.json')
        custom_action_json = open_json(custom_action_path)

        # replace parameters in custom action with input json
        inserted_inputs = insert_inputs(custom_action_json)
        if inserted_inputs is None:
            action_logger.error('Could not insert inputs for custom action with name: ' + custom_action_name)
            return None
        custom_action_json.update(inserted_inputs)
        return custom_action_json

    except IOError:
        action_logger.error('Could not open custom actions file with path: ' + custom_action_path)
        return None


def insert_inputs(custom_action_json):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    # create result json
    result_json = {'parameters': {}}
    try:
        # get possible inputs for validation
        possible_inputs_json = open_json(settings.POSSIBLE_INPUTS_PATH)
    except IOError:
        action_logger.error('Could not open possible inputs file with path: ' + settings.POSSIBLE_INPUTS_PATH)
        return None

    # add all defined inputs to result json
    for action_input in possible_inputs_json['inputs']:
        result_json['parameters'].update({action_input: []})
        if action_input in custom_action_json['parameters']:
            for custom_input in custom_action_json['parameters'][action_input]:
                replaced_input = replace_input(custom_input, action_input)
                if replace_input is None:
                    action_logger.error('Could not replace input from type {}'.format(action_input))
                    return None
                result_json['parameters'][action_input].append(replaced_input)

    return result_json


def replace_input(custom_input, action_input):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    try:
        # validation input file
        input_path = os.path.join(settings.INPUTS_PATH, action_input + '.json')
        input_json = open_json(input_path)
    except IOError:
        action_logger.error('Could not open validation input file with path: ' + input_path)
        return None

    result_json = {}
    result_json.update({'name': custom_input['name']})
    result_json.update({'description': custom_input['description']})

    # recursively replace parameters in validation input with custom input
    replace_parameters = replace_recursive(custom_input['value'], input_json['value'])
    if replace_parameters is None:
        action_logger.error('Could not replace parameters in validation input file with path: ' + input_path)
        return None
    result_json.update({'value': replace_parameters})
    return result_json


def replace_recursive(custom_input, input_json):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    if type(custom_input) is not dict:
        return custom_input
    for key, value in input_json.items():
        if key in custom_input:
            replacement_value = replace_recursive(custom_input[key], value)
            if replacement_value is None:
                return None
            if type(input_json[key]) is list and type(custom_input[key]) is not list:
                if replacement_value not in input_json[key]:
                    action_logger.error('Could not find replacement value in possible inputs for key: ' + key)
                    return None
                else:
                    input_json[key] = replacement_value
            else:
                input_json[key] = replacement_value

    return input_json


def replace_icons(actions_json):
    for action in actions_json['actions']:
        if 'icon' in action:
            if action['icon'] != "":
                # replace icon with corresponding svg link
                icon_path = '/servestatic/' + 'icon/' + action['icon']
                action.update({'icon': icon_path})

    return actions_json

