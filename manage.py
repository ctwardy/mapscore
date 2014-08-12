#!/usr/bin/env python
import sys

from django.core.management import execute_manager


ERR_MSG = "\
ERROR: Can't find the file 'settings.py' in the directory containing {}.\n\
\tIt appears you've customized things.\n\
\tYou'll have to run django-admin.py, passing it your settings module.\n"

try:
    # settings module should be in current directory
    import settings
except ImportError:
    sys.stderr.write(ERR_MSG.format(__file__))
    sys.exit(1)


if __name__ == "__main__":
    execute_manager(settings)
