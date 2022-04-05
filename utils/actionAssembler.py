from django.conf import settings
from utils.miscellaneous import open_json
from utils.fileSystem import check_image_exists
import os

# import all dynamic parameters
import dynamic_functions as functions


# TODO add exception handling
def assemble_actions(session_id):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
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
            inserted_custom_action = insert_action(action, session_id=session_id)
            if inserted_custom_action is None:
                action_logger.error('Could not insert custom action with name: ' + action)
                return None
            add_action_json_to_actions(actions_json=actions_json, action_json=inserted_custom_action,
                                       available=action_availability)

        # clean actions json from custom, base and init actions
        clean_action_json(actions_json)
        actions_json = replace_icons(actions_json)

        return actions_json
    except IOError:
        action_logger.error('Could not open actions file with path: ' + settings.ACTIONS_PATH)
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


def insert_action(custom_action_name, session_id, actions_path=settings.CUSTOM_ACTIONS_PATH):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
    # check if custom action exists
    try:
        custom_action_path = os.path.join(actions_path, custom_action_name + '.json')
        custom_action_json = open_json(custom_action_path)

        # replace parameters in custom action with input json
        inserted_inputs = insert_inputs(custom_action_json, session_id)
        if inserted_inputs is None:
            action_logger.error('Could not insert inputs for custom action with name: ' + custom_action_name)
            return None
        custom_action_json.update(inserted_inputs)
        return custom_action_json

    except IOError:
        action_logger.error('Could not open custom actions file with path: ' + custom_action_path)
        return None


def insert_inputs(custom_action_json, session_id):
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
                replaced_input = replace_input(custom_input, action_input, session_id)
                if replace_input is None:
                    action_logger.error('Could not replace input from type {}'.format(action_input))
                    return None
                result_json['parameters'][action_input].append(replaced_input)

    return result_json


def replace_input(custom_input, action_input, session_id):
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
    replace_parameters = replace_recursive(custom_input['value'], input_json['value'], session_id)
    if replace_parameters is None:
        action_logger.error('Could not replace parameters in validation input file with path: ' + input_path)
        return None
    result_json.update({'value': replace_parameters})
    return result_json


def replace_recursive(custom_input, input_json, session_id):
    action_logger = settings.ACTION_ASSEMBLER_LOGGER
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
                    action_logger.error('Could not find replacement value in possible inputs for key: ' + key)
                    return None

            # check if replacement value is a dynamic value
            replacement_value = replace_dynamic_values(replacement_value, session_id)
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
        if value.startswith('$dynamic:'):
            value = evaluate_dynamic_values(value.split(':')[-1], session_id)
    elif type(value) is list:
        for index, item in enumerate(value):
            if type(item) is str:
                if item.startswith('$dynamic:'):
                    value[index] = evaluate_dynamic_values(item.split(':')[-1], session_id)

    return value


def evaluate_dynamic_values(dynamic_value, session_id):
    if not check_image_exists(session_id):
        return "N/A"
    dynamic_function_method = getattr(functions, dynamic_value)
    function_result = dynamic_function_method(session_id)
    return function_result
