"""Context processors for the videos app.
Available in every template because we added videos.context_processors.notifications to settings.py. 
"""

def notifications(request):
    """Provide unread notification count to every template."""
    if request.user.is_authenticated:
        return {
            'unread_count': request.user.notifications.filter(is_read=False).count(),
        }
    return {'unread_count': 0}
