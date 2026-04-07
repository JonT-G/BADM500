"""
Root URL configuration for the BADM500 project. Which URL goes where.
So all URL routing goes in videos/url.py.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls), # Django admin site, for managing users and videos
    path('', include('videos.urls')), # or just hand over to videos/urls.py for routing
]

# used to enable fecthing the mediafiles back (like avater, videos, etc.) so we can see them intead of some error or 404 for images. 
# In real production have a real web server like nginx or apache. Maybe not needed for size of project?
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
