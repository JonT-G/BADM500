"""
Creates test videos. Wipes existing videos first.
Requires users to exist — run test_users.py first.

Usage: python test_data/test_videos.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from django.contrib.auth.models import User
from videos.models import Video

Video.objects.all().delete()
print('  Wiped all videos.')

alice   = User.objects.get(username='alice')
bob     = User.objects.get(username='bob')
charlie = User.objects.get(username='charlie')

# alice's videos
Video.objects.create(author=alice, title='Morning Routine Vlog',      description='My daily morning routine.',     visibility='public',   duration=300)
Video.objects.create(author=alice, title='How to Make Coffee',         description='The perfect cup of coffee.',    visibility='public',   duration=300)
Video.objects.create(author=alice, title='Private Draft',              description='Not published yet.',            visibility='private',  duration=300)

# bob's videos
Video.objects.create(author=bob,   title='Gaming Highlights #1',      description='Best plays from this week.',    visibility='public',   duration=300)
Video.objects.create(author=bob,   title='Road Trip Across Norway',   description='Van life diaries.',             visibility='public',   duration=300)

# charlie's videos
Video.objects.create(author=charlie, title='Study With Me - 2 Hours', description='Cozy library ambience.',        visibility='public',   duration=300)
Video.objects.create(author=charlie, title='Unlisted Test Video',      description='Only via direct link.',         visibility='unlisted', duration=300)

print(f'  Created {Video.objects.count()} videos.')
