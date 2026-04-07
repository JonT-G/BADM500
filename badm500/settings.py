"""Django settings for the video-sharing platform."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
#just for cookies and sessions, but should be random and secret if real production. Maybe change?
SECRET_KEY = 'ThisIsForCokkiesAndSessionsOnly'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
#https://docs.djangoproject.com/en/6.0/ref/contrib/
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'videos',
]

# code that runs on every request, in order.
#https://docs.djangoproject.com/en/6.0/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # adds security headers
    'django.contrib.sessions.middleware.SessionMiddleware',    # loads the session on each request
    'django.middleware.csrf.CsrfViewMiddleware',               # protects forms from cross-site attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware', # attaches request.user
    'django.contrib.messages.middleware.MessageMiddleware',    # attaches flash messages
]

ROOT_URLCONF = 'badm500.urls'
#match URL from badm500/urls.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'videos.notifications.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'badm500.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}

# Password validation. Built-in django rules.
# - password can't be too similar to your username
# - must be at least 8 characters
# - can't be a common password like "password123"
# - can't be all numbers
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', 
    },
]

# language and Timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True

# Static & media files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth redirects
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

#for auto-generating IDs for models. built-in Django
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
