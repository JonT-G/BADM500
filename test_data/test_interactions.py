"""
Creates likes, comments, comment votes, subscriptions, watch history, and watch later.
Requires users and videos to exist — run test_users.py and test_videos.py first.

Usage: python test_data/test_interactions.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from django.contrib.auth.models import User
from videos.models import Comment, CommentVote, Like, Subscription, Video, WatchHistory, WatchLater

alice   = User.objects.get(username='alice')
bob     = User.objects.get(username='bob')
charlie = User.objects.get(username='charlie')

public_videos = list(Video.objects.filter(visibility='public'))

# ---- Subscriptions ----
Subscription.objects.create(subscriber=bob,     channel=alice)
Subscription.objects.create(subscriber=charlie, channel=alice)
Subscription.objects.create(subscriber=charlie, channel=bob)
Subscription.objects.create(subscriber=alice,   channel=bob)
print('  Created 4 subscriptions.')

# ---- Likes (everyone likes every public video they did not make) ----
for video in public_videos:
    for user in [alice, bob, charlie]:
        if user != video.author:
            Like.objects.create(video=video, user=user, is_like=True)

# bob dislikes alice's coffee video specifically
coffee = Video.objects.get(title='How to Make Coffee')
Like.objects.filter(video=coffee, user=bob).update(is_like=False)
print('  Created likes.')

# ---- Comments (one per public video from a non-author) ----
comments = []
for video in public_videos:
    commenter = next(u for u in [alice, bob, charlie] if u != video.author)
    comment = Comment.objects.create(
        video=video,
        author=commenter,
        text=f'Great video "{video.title}"! Really enjoyed it.',
    )
    comments.append(comment)
print(f'  Created {len(comments)} comments.')

# ---- Comment votes (alice upvotes, bob downvotes) ----
for comment in comments:
    for user in [alice, bob, charlie]:
        if user != comment.author:
            CommentVote.objects.create(comment=comment, user=user, is_upvote=(user == alice))
print('  Created comment votes.')

# ---- Watch history and watch later for alice ----
WatchHistory.objects.create(user=alice, video=public_videos[0])
WatchHistory.objects.create(user=alice, video=public_videos[1])
WatchHistory.objects.create(user=alice, video=public_videos[2])
WatchHistory.objects.create(user=alice, video=public_videos[3])

WatchLater.objects.create(user=alice, video=public_videos[2])
WatchLater.objects.create(user=alice, video=public_videos[3])
WatchLater.objects.create(user=alice, video=public_videos[4])
print('  Created watch history and watch later for alice.')
