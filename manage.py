#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import argparse
import json
from utils.configure import configure_server_settings


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PiXS.settings')
    argv = sys.argv
    # custom command line arguments
    cmd = argv[1] if len(argv) > 1 else None
    if cmd in ['runserver']:  # limit extra arguments to runserver command
        from django.conf import settings
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--mode', default='dev')
        parser.add_argument('--config', default=settings.CONFIG_FILE_PATH)
        args, argv = parser.parse_known_args(argv)
        server_config = json.loads(open(args.config).read())
        configure_server_settings(args.mode, server_config)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(argv)


if __name__ == '__main__':
    main()
