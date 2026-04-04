"""URL routing for the videos app."""

from django.urls import path
from . import views
from .streaming import stream_video

# URL patterns for the videos app. Maps URL paths to view functions.
# <int:pk> captures the number (integer) and passes it as pk= to the view
# name='watch' lets templates do {% url 'watch' video.pk %} instead of hardcoding /watch/5/.
# also lets you use {% url %} tags in templates.

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('watch/<int:pk>/', views.watch, name='watch'),
    path('upload/', views.upload, name='upload'),
    path('profile/<str:username>/', views.profile, name='profile'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Actions
    path('like/<int:pk>/', views.toggle_like, name='like'),
    path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
    path('save/<int:pk>/', views.toggle_watch_later, name='toggle_save'),
    path('comment-vote/<int:pk>/', views.vote_comment, name='vote_comment'),

    # Library
    path('history/', views.history, name='history'),
    path('watch-later/', views.watch_later_list, name='watch_later'),
    path('liked/', views.liked_videos, name='liked_videos'),
    path('notifications/', views.notifications_list, name='notifications'),

    # Management
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete/<int:pk>/', views.delete_video, name='delete_video'),

    # Streaming
    path('stream/<int:pk>/', stream_video, name='stream_video'),
]
