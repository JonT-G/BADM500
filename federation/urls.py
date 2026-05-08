"""
URL routing for the federation (ActivityPub) app.

Module defines the URL patterns for the federation app, which includes:
- Actor URLs: /users/<username>, /users/<username>/inbox, etc.
- WebFinger: /.well-known/webfinger
"""

from django.urls import path

from .webfinger import webfinger
from . import views

app_name = "federation"

actor_patterns = [
    path("users/<str:username>", views.actor, name="actor"),
    path("users/<str:username>/inbox", views.inbox, name="inbox"),
    path("users/<str:username>/outbox", views.outbox, name="outbox"),
    path("users/<str:username>/followers", views.followers, name="followers"),
    path("users/<str:username>/following", views.following, name="following"),
]

urlpatterns = actor_patterns + [
    path(".well-known/webfinger", webfinger, name="webfinger"),
]


urlpatterns = actor_patterns + urlpatterns
