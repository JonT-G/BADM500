"""
Just so we debuggin abilities in admin interface for RemoteFollower model, which is where followers on other servers are stored.
"""

from django.contrib import admin
from .models import RemoteFollower

admin.site.register(RemoteFollower)
