"""App configuration for the videos app. This is where vidoes in INSTALLED_APPS in settings.py pounts to.
Sets ID type for all models in the app. Check settings for more
"""
from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'
