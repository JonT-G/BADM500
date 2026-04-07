"""
App configuration for the videos app. 
This is where videos in INSTALLED_APPS in settings.py points to.
So when server starts it sees all the apps in INSTALLED_APPS and loads them.
"""
from django.apps import AppConfig

class VideosConfig(AppConfig):
    name = 'videos'
