#!/usr/bin/env python
"""
Just run this if no need for docker. 
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

def run(*args):
    subprocess.check_call([PY] + list(args), cwd=BASE_DIR)

def main():
    print('=== BADM500 — Video Sharing Platform ===\n')

    # 1. Install dependencies
    run('-m', 'pip', 'install', '-q', '-r', 'requirements.txt')

    # 2. Run database migrations
    run('manage.py', 'migrate', '--noinput')

    # 3. Start development server
    run('manage.py', 'runserver', '8080')

if __name__ == '__main__':
    main()
