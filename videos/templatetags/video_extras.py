"""Custom template filters for the videos app.
Allows the templates to use {{ video.duration|format_duration }}.
So converts 272 to 4:32, and 3672 to 1:01:12.
"""
from django import template
register = template.Library()

@register.filter
def format_duration(seconds):
    """Convert seconds to 'M:SS' or 'H:MM:SS' format for duration badges."""
    if seconds is None:
        return ''
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    return f'{minutes}:{secs:02d}'
