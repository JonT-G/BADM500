"""
WSGI: Web Server Gateway Interface.

Standard way python web apps talk to web servers.
Check the formal documentation:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
application = get_wsgi_application()
