#!/usr/bin/env python
"""
just a shortcut to run all manage.py commands in one go.  
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

def run(*args):
    subprocess.check_call([PY] + list(args), cwd=BASE_DIR)

def main():
    print(' Running BADM500: Video Sharing Platform\n')
    # install dependencies if needed
    run('-m', 'pip', 'install', '-q', '-r', 'requirements.txt')

    # begin database setup, skip if already setup
    run('manage.py', 'migrate', '--noinput')

    print('\nLive server: http://127.0.0.1:8080/')
    print('Admin panel for debugging: http://127.0.0.1:8080/admin/\n')
    run('manage.py', 'runserver', '8080')

if __name__ == '__main__':
    main()
