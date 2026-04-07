#!/usr/bin/env python
"""Basically sets up migration files and creates database tables in db.sqlite3, it crashes without it."""
import os
import sys

def main():
    #Run administrative tasks
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. maybe you need to install it?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
