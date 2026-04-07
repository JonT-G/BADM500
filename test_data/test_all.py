"""
Wipes everything and runs all test scripts in order.
Shortcut for: test_users, test_videos, test_interactions, test_notifications.

Usage: python test_data/test_all.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from videos.models import Comment, Like, Notification, Video

print('\n=== Loading all test data ===\n')

exec(open('test_data/test_users.py').read())
exec(open('test_data/test_videos.py').read())
exec(open('test_data/test_interactions.py').read())
exec(open('test_data/test_notifications.py').read())

print('\n' + '=' * 45)
print('  Done. Login credentials:')
print('  admin   / admin123  (superuser — /admin/)')
print('  alice   / alice123')
print('  bob     / bob123')
print('  charlie / charlie123')
print('=' * 45)
print(
    f'  {Video.objects.count()} videos | '
    f'{Comment.objects.count()} comments | '
    f'{Like.objects.count()} likes | '
    f'{Notification.objects.count()} notifications'
)
print('=' * 45 + '\n')
