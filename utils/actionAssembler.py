from django.conf import settings
from utils.miscellaneous import open_json
from utils.fileSystem import check_image_exists
from copy import deepcopy
import os
import logging

# import all dynamic parameters
import dynamic_functions as functions

from inspect import signature


def assemble_actions(session_id):
    try:
        actions_json = open_json(settings.ACTIONS_PATH)
        actions_json['actions'] = []

        action_availability = True
        # insert all init actions
        for action in actions_json['initActions']:
            init_action = os.path.join(settings.BASE_ACTIONS_PATH, action + '.json')
            init_action_json = open_json(init_action)
            add_action_json_to_actions(actions_json=actions_json, action_json=init_action_json,
                                       available=action_availability)

        if not check_image_exists(session_id=session_id):
            action_availability = False

        # insert all base actions
        for action in actions_json['baseActions']:
            base_action_path = os.path.join(settings.BASE_ACTIONS_PATH, action + '.json')
            base_action_json = open_json(base_action_path)
            add_action_json_to_actions(actions_json=actions_json, action_json=base_action_json,
                                       available=action_availability)

        # insert all custom actions into actions
        for action in actions_json['customActions']:
            inserted_custom_action = insert_action(action, session_id=session_id,
                                                   actions_path=settings.CUSTOM_ACTIONS_PATH)
            if inserted_custom_action is None:
                logging.error('Could not insert custom action with name: ' + action)
                return None
            add_action_json_to_actions(actions_json=actions_json, action_json=inserted_custom_action,
                                       available=action_availability)

        # clean actions json from custom, base and init actions
        clean_action_json(actions_json)
        actions_json = replace_icons(actions_json)

        return actions_json
    except IOError:
        logging.error('Could not open actions file with path: ' + settings.ACTIONS_PATH)
        return None


def add_action_json_to_actions(actions_json, action_json, available):
    action_json['available'] = available
    actions_json['actions'].append(action_json)


def clean_action_json(actions_json):
    # remove custom, base and init actions
    if 'customActions' in actions_json:
        del actions_json['customActions']
    if 'baseActions' in actions_json:
        del actions_json['baseActions']
    if 'initActions' in actions_json:
        del actions_json['initActions']


def insert_action(custom_action_name, session_id, actions_path):
    # check if custom action exists
    try:
        custom_action_path = os.path.join(actions_path, custom_action_name + '.json')
        custom_action_json = open_json(custom_action_path)

        # replace parameters in custom action with input json
        inserted_inputs = insert_inputs(custom_action_json, session_id)
        if inserted_inputs is None:
            logging.error('Could not insert inputs for custom action with name: ' + custom_action_name)
            return None
        custom_action_json.update(inserted_inputs)
        return custom_action_json

    except IOError:
        logging.error('Could not open custom actions file with path: ' + custom_action_path)
        return None


def insert_inputs(custom_action_json, session_id):
    # create result json
    result_json = {'parameters': {}}
    try:
        # get possible inputs for validation
        possible_inputs_json = open_json(settings.POSSIBLE_INPUTS_PATH)
    except IOError:
        logging.error('Could not open possible inputs file with path: ' + settings.POSSIBLE_INPUTS_PATH)
        return None

    # add all defined inputs to result json
    for action_input in possible_inputs_json['inputs']:
        result_json['parameters'].update({action_input: []})
        if action_input in custom_action_json['parameters']:
            for custom_input in custom_action_json['parameters'][action_input]:
                replaced_input = replace_input(custom_input, action_input, session_id)
                if replace_input is None:
                    logging.error('Could not replace input from type {}'.format(action_input))
                    return None
                result_json['parameters'][action_input].append(replaced_input)

    return result_json


def replace_input(custom_input, action_input, session_id):
    try:
        # validation input file
        input_path = os.path.join(settings.INPUTS_PATH, action_input + '.json')
        input_json = open_json(input_path)
    except IOError:
        logging.error('Could not open validation input file with path: ' + input_path)
        return None

    result_json = {}
    result_json.update({'name': custom_input['name']})
    result_json.update({'description': custom_input['description']})

    # recursively replace parameters in validation input with custom input
    replace_parameters = replace_recursive(custom_input['value'], input_json['value'], session_id)
    if replace_parameters is None:
        logging.error('Could not replace parameters in validation input file with path: ' + input_path)
        return None
    result_json.update({'value': replace_parameters})
    return result_json


def replace_recursive(custom_input, input_json, session_id):
    if type(custom_input) is not dict:
        return custom_input
    for key, value in input_json.items():
        if key in custom_input:
            replacement_value = replace_recursive(custom_input[key], value, session_id)
            if replacement_value is None:
                return None
            if type(input_json[key]) is list and type(custom_input[key]) is not list:
                # check if replacement value is a possible input value
                if replacement_value not in input_json[key]:
                    logging.error('Could not find replacement value in possible inputs for key: ' + key)
                    return None

            # check if replacement value is a dynamic value
            replacement_value = replace_dynamic_values(replacement_value, session_id)
            if replacement_value is None:
                logging.error("Could not replace dynamic value in input file")
                return None
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


def replace_dynamic_values(value, session_id):
    if type(value) is str:
        if value.startswith(functions.DYNAMIC_START_SEQUENCE):
            value = evaluate_dynamic_values(value.split(functions.DYNAMIC_SEPARATOR)[1:], session_id)
    elif type(value) is list:
        result_list = deepcopy(value)
        for index, value in enumerate(value):
            if type(value) is str:
                if value.startswith(functions.DYNAMIC_START_SEQUENCE):
                    values = value.split(functions.DYNAMIC_SEPARATOR)[1:]
                    try:
                        result_list[index] = evaluate_dynamic_values(values, session_id)
                    except ValueError as e:
                        return None
        return result_list

    # default return if value is not a dynamic value
    return value


def evaluate_dynamic_values(values, session_id):
    if not check_image_exists(session_id):
        return "N/A"

    if values[0] == "m":
        print(values[0])
    visited_arguments, function_result = follow_tree(value=getattr(functions, values[0]), values=values[1:], session_id=session_id)
    if not visited_arguments == len(values) - 1:
        raise ValueError('Could not evaluate all arguments in dynamic value')
    return function_result


def follow_tree(value, values, session_id) -> (int, list):
    # -1 because every function has at least one argument (the session_id)
    number_of_arguments = len(signature(value).parameters) - 1  # except session_id
    if number_of_arguments == 0:
        return 0, make_call(value, session_id)
    if check_for_terminal(number_of_arguments, values):
        stripped_values = strip_terminal_values(number_of_arguments, values)
        return len(stripped_values), make_call(value, session_id, stripped_values)

    arguments = []
    visited_arguments = 0
    while visited_arguments < len(values):
        new_visited_args, new_arguments = follow_tree(value=getattr(functions, values[visited_arguments]),
                                                      values=values[visited_arguments + 1:],
                                                      session_id=session_id)
        arguments.append(new_arguments)
        visited_arguments += new_visited_args + 1

    return visited_arguments, make_call(value, session_id, arguments)


def check_for_terminal(number_of_arguments, values) -> bool:
    for number_of_arguments in range(number_of_arguments):
        if not (values[number_of_arguments].startswith(functions.DYNAMIC_TERMINAL_INDICATOR) and \
                values[number_of_arguments].endswith(functions.DYNAMIC_TERMINAL_INDICATOR)):
            return False
    return True


def strip_terminal_values(number_of_arguments, values):
    stripped_values = []
    for value in values[:number_of_arguments]:
        stripped_values.append(value[1:-1])
    return stripped_values


def make_call(method, session_id, arguments=[]):
    try:
        result = method(session_id, *arguments)
    except Exception as e:
        raise ValueError('Could not evaluate dynamic value')
    return result
