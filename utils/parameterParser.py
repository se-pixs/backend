from django.conf import settings
import logging
import os
from utils.miscellaneous import open_json


def parseParameters(action_parameters):
    """
    Parses the parameters given in the command line.
    """
    parameters = action_parameters['parameters']
    parser_logger = logging.getLogger('parser')
    try:
        # get possible inputs for validation
        possible_inputs_json = open_json(settings.POSSIBLE_INPUTS_PATH)
    except IOError:
        parser_logger.error('Could not open possible inputs file with path: ' + settings.POSSIBLE_INPUTS_PATH)
        return None

    result_params = parseInputsToDict(parameters, possible_inputs_json['inputs'])

    # validate parameters
    validateParameter(result_params, action_parameters['name'], possible_inputs_json["inputs"])

    return result_params


def parseInputsToDict(params, possible_inputs):
    result_dict = {}
    for possible_input in possible_inputs:
        if possible_input in params:
            for param in params[possible_input]:
                result_dict[param['name']] = param['value']

    return result_dict


def validateParameter(parameters, action_name, possible_inputs):
    """
    Validates the parameters
    """
    parser_logger = logging.getLogger('parser')
    validate_json_path = os.path.join(settings.CUSTOM_ACTIONS_PATH, action_name + '.json')
    try:
        validate_json = open_json(validate_json_path)
        validate_json = parseInputsToDict(validate_json['parameters'], possible_inputs)
    except IOError:
        parser_logger.error('Could not open validation file with path: ' + validate_json_path)

    for name, value in parameters.items():
        if name in validate_json:
            validate_value = validate_json[name]
            # type check
            if 'type' in validate_value:
                if validate_value['type'] == 'integer' and not isinstance(value, int):
                    raise ValueError('Parameter ' + name + ' is not an integer')
                elif validate_value['type'] == 'float' and not isinstance(value, float):
                    raise ValueError('Parameter ' + name + ' is not a float')
                elif validate_value['type'] == 'string' and not isinstance(value, str):
                    raise ValueError('Parameter ' + name + ' is not a string')

            # range check
            if 'range' in validate_value:
                # type check
                if type(value) is str:
                    if value not in validate_value['range']:
                        raise ValueError('Value ' + value + ' is not in range of ' + name + '.')
                else:
                    if value < validate_value['range'][0] or value > validate_value['range'][-1]:
                        raise ValueError('Value ' + str(value) + ' is not in range of ' + name + '.')

            else:
                if 'min' in validate_value:
                    if value < validate_value['min']:
                        raise ValueError('Value ' + str(value) + ' is smaller than minimum of ' + name + '.')
                if 'max' in validate_value:
                    if value > validate_value['max']:
                        raise ValueError('Value ' + str(value) + ' is bigger than maximum of ' + name + '.')

            # step value check
            if 'step' in validate_value:
                if 'min' in validate_value:
                    if (validate_value['min'] + value) % validate_value['step'] != 0:
                        raise ValueError('Value ' + str(value) + ' is not a multiple of ' + name + '.')
                else:
                    if value % validate_value['step'] != 0:
                        raise ValueError('Value ' + str(value) + ' is not a multiple of ' + name + '.')

        else:
            raise Exception('Parameter ' + name + ' is not valid for action ' + action_name)
