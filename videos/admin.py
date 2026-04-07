"""
Django admin configuration for all video-platform models. Built-in django feature
A full UI browser to view and manage all data.
When doing "python run.py" in terminal a link to "admin panel" is printed and clickable.
Username: admin
Password: admin123
"""
from django.contrib import admin

from .models import (
    Comment, CommentVote, Like, Notification, Profile, Subscription,
    Video, WatchHistory, WatchLater,
)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'visibility', 'views', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'actor', 'verb', 'video', 'is_read', 'created_at']
    list_filter = ['verb', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'actor__username']

admin.site.register([Comment, Like, Subscription, CommentVote, Profile, WatchHistory, WatchLater])
