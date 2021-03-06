from django.conf import settings
import os
import logging


def configure_server_settings(mode, server_settings):
    """
    Configure server settings.
    Note: To enforce failure on mal-configured settings, we do assignments in a static way
    """
    logging.info('server_settings')

    if mode == 'development' or 'dev':
        mode = 'development'
        logging.info('Configuring server settings for development mode')

        server_setting = server_settings['development']
        settings.SESSION_EXPIRATION_TIME = server_setting['SESSION_EXPIRATION_TIME']
        settings.MAX_REVERSE_STACK_SIZE = server_setting['MAX_REVERSE_STACK_SIZE']
        settings.CONFIG_PATH = server_setting['CONFIG_PATH']
        settings.ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['ACTIONS'])
        settings.CUSTOM_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['CUSTOM_ACTIONS'])
        settings.BASE_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['BASE_ACTIONS'])
        settings.INIT_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['INIT_ACTIONS'])
        settings.INPUTS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['INPUTS'])
        settings.POSSIBLE_INPUTS_PATH = os.path.join(
            settings.INPUTS_PATH, server_setting['POSSIBLE_INPUTS'])
        settings.IMAGES_ROOT_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['IMAGES_ROOT'])
        settings.REVERSE_STACK_PATH = server_setting[
            'REVERSE_STACK_PATH']  # absolute path is different for every session
        settings.TEMP_PATH = server_setting[
            'TEMP_PATH']  # absolute path is different for every session
        settings.ICONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['ICONS'])
        settings.ALLOWED_ORIGIN = server_setting['ALLOWED_ORIGIN']

        # logging constants
        settings.LOGGING_PATH = server_setting['LOGGING_PATH']
        settings.ACTION_ASSEMBLER_LOGGING_PATH = os.path.join(settings.LOGGING_PATH,
                                                              server_setting['ACTION_ASSEMBLER_LOG_PATH'])

        logging.info('Server settings configured for development mode')

    elif mode == 'production' or 'prod':
        mode = 'production'
        logging.info('Configuring server settings for production mode')
        server_setting = server_settings['production']
        settings.SESSION_EXPIRATION_TIME = server_setting['SESSION_EXPIRATION_TIME']
        settings.MAX_REVERSE_STACK_SIZE = server_setting['MAX_REVERSE_STACK_SIZE']
        settings.CONFIG_PATH = server_setting['CONFIG_PATH']
        settings.ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['ACTIONS'])
        settings.CUSTOM_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['CUSTOM_ACTIONS'])
        settings.BASE_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['BASE_ACTIONS'])
        settings.INIT_ACTIONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['INIT_ACTIONS'])
        settings.INPUTS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['INPUTS'])
        settings.POSSIBLE_INPUTS_PATH = os.path.join(
            settings.INPUTS_PATH, server_setting['POSSIBLE_INPUTS'])
        settings.IMAGES_ROOT_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['IMAGES_ROOT'])
        settings.REVERSE_STACK_PATH = server_setting[
            'REVERSE_STACK_PATH']  # absolute path is different for every session
        settings.TEMP_PATH = server_setting[
            'TEMP_PATH']  # absolute path is different for every session
        settings.ICONS_PATH = os.path.join(
            settings.CONFIG_PATH, server_setting['ICONS'])
        settings.ALLOWED_ORIGIN = server_setting['ALLOWED_ORIGIN']

        # logging constants
        settings.LOGGING_PATH = server_setting['LOGGING_PATH']
        settings.ACTION_ASSEMBLER_LOGGING_PATH = os.path.join(settings.LOGGING_PATH,
                                                              server_setting['ACTION_ASSEMBLER_LOG_PATH'])

        logging.info('Server settings configured for production mode')
        logging.info('Configuring action assembler for production mode')
    else:
        logging.error('Invalid mode: {}'.format(mode))
        raise ValueError('Invalid mode: {}'.format(mode))

    # further configure steps
    configure_actionAssembler(mode)


def configure_actionAssembler(mode):
    logging.info('Configuring action assembler')

    logging.info(
        'ActionAssembler initialized with mode: {}'.format(mode))
    logging.info('Configuring action assembler logger')
