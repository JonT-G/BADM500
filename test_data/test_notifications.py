"""
Creates test notifications. Wipes existing notifications first.
Requires users and videos to exist — run test_users.py and test_videos.py first.

Usage: python test_data/test_notifications.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from django.contrib.auth.models import User
from videos.models import Notification, Video

Notification.objects.all().delete()
print('  Wiped all notifications.')

alice   = User.objects.get(username='alice')
bob     = User.objects.get(username='bob')
charlie = User.objects.get(username='charlie')

alice_video = Video.objects.filter(author=alice, visibility='public').first()
bob_video   = Video.objects.filter(author=bob,   visibility='public').first()

# alice gets 4 notifications (one of each type)
Notification.objects.create(recipient=alice, actor=bob,     verb='liked',      video=alice_video)
Notification.objects.create(recipient=alice, actor=charlie, verb='commented',  video=alice_video)
Notification.objects.create(recipient=alice, actor=bob,     verb='subscribed', video=None)
Notification.objects.create(recipient=alice, actor=charlie, verb='upvoted',    video=alice_video)

# bob gets 2 notifications
Notification.objects.create(recipient=bob, actor=alice,   verb='liked',     video=bob_video)
Notification.objects.create(recipient=bob, actor=charlie, verb='commented', video=bob_video)

print('  Created 6 notifications (4 for alice, 2 for bob).')
print('  Log in as alice to see the notification bell in action.')
