#!/usr/bin/env python
"""
One-command startup for BADM500.

    python run.py

Installs dependencies, runs migrations, seeds sample data (if empty),
and starts the development server on http://127.0.0.1:8080.
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
    print('[1/4] Installing dependencies...')
    run('-m', 'pip', 'install', '-q', '-r', 'requirements.txt')

    # 2. Run database migrations
    print('[2/4] Running database migrations...')
    run('manage.py', 'migrate', '--noinput')

    # 3. Seed sample data if database is empty
    print('[3/4] Checking database...')
    result = subprocess.run(
        [PY, '-c',
         'import os, django; '
         'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "badm500.settings"); '
         'django.setup(); '
         'from django.contrib.auth.models import User; '
         'print(User.objects.count())'],
        capture_output=True, text=True, cwd=BASE_DIR,
    )
    count = result.stdout.strip()
    if count == '0':
        print('       Database is empty — seeding sample data...')
        run('seed_data.py')
    else:
        print(f'       Database has {count} users — skipping seed.')

    # 4. Start development server
    print('[4/4] Starting server...\n')
    print('       http://127.0.0.1:8080\n')
    run('manage.py', 'runserver', '8080')


if __name__ == '__main__':
    main()
