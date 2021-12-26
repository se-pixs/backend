from django.conf import settings
import os
import logging


def configure_server_settings(mode, server_settings):
    """
    Configure server settings.
    Note: To enforce failure on mal-configured settings, we do assignments in a static way
    """
    if mode == 'development' or 'dev':
        logging.info('Configuring server settings for development mode')
        server_setting = server_settings['development']
        settings.SESSION_EXPIRATION_TIME = server_setting['SESSION_EXPIRATION_TIME']
        settings.CONFIG_PATH = server_setting['CONFIG_PATH']
        settings.ACTIONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['ACTIONS'])
        settings.CUSTOM_ACTIONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['CUSTOM_ACTIONS'])
        settings.INPUTS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['INPUTS'])
        settings.POSSIBLE_INPUTS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['POSSIBLE_INPUTS'])
        settings.IMAGES_ROOT_PATH = os.path.join(settings.CONFIG_PATH, server_setting['IMAGES_ROOT'])
        settings.ICONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['ICONS'])
        logging.info('Server settings configured for development mode')
    elif mode == 'production' or 'prod':
        logging.info('Configuring server settings for production mode')
        server_setting = server_settings['production']
        settings.SESSION_EXPIRATION_TIME = server_setting['SESSION_EXPIRATION_TIME']
        settings.CONFIG_PATH = server_setting['CONFIG_PATH']
        settings.ACTIONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['ACTIONS'])
        settings.CUSTOM_ACTIONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['CUSTOM_ACTIONS'])
        settings.INPUTS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['INPUTS'])
        settings.POSSIBLE_INPUTS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['POSSIBLE_INPUTS'])
        settings.IMAGES_ROOT_PATH = os.path.join(settings.CONFIG_PATH, server_setting['IMAGES_ROOT'])
        settings.ICONS_PATH = os.path.join(settings.CONFIG_PATH, server_setting['ICONS'])
        logging.info('Server settings configured for production mode')
    else:
        logging.error('Invalid mode: {}'.format(mode))
        raise ValueError('Invalid mode: {}'.format(mode))
