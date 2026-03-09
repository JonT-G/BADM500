"""
Seed script to populate the database with sample data.
Run with: python manage.py shell < seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badm500.settings')
django.setup()

from django.contrib.auth.models import User
from videos.models import Video, Comment, Subscription
from django.utils import timezone
from datetime import timedelta

# Create users
users_data = [
    ('maria', 'maria@example.com', 'Maria', 'Jensen'),
    ('jake', 'jake@example.com', 'Jake', 'Miller'),
    ('sarah', 'sarah@example.com', 'Sarah', 'Anderson'),
    ('tom', 'tom@example.com', 'Tom', 'Williams'),
    ('lisa', 'lisa@example.com', 'Lisa', 'Brown'),
    ('kevin', 'kevin@example.com', 'Kevin', 'Davis'),
    ('emma', 'emma@example.com', 'Emma', 'Wilson'),
    ('nina', 'nina@example.com', 'Nina', 'Taylor'),
]

users = {}
for username, email, first, last in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': first,
            'last_name': last,
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    users[username] = user

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@badm500.local',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print('Admin user created (admin / admin123)')

now = timezone.now()

# Create sample videos, just show UI.
videos_data = [
    ('maria', 'Trip to the Zoo - We Fed the Giraffes!',
     'We took the kids to the city zoo last weekend and it was amazing!',
     2413, now - timedelta(days=3)),
    ('jake', 'Making Grandma\'s Secret Pasta Recipe',
     'Finally got grandma to share her famous pasta recipe. Here\'s how to make it!',
     1100, now - timedelta(days=5)),
    ('sarah', 'Road Trip Across Norway - Van Life Diaries',
     'Our epic road trip across the Norwegian fjords in our converted van.',
     890, now - timedelta(weeks=1)),
    ('tom', 'I Beat the Hardest Boss on My First Try',
     'You won\'t believe this epic gaming moment! First attempt and nailed it.',
     3700, now - timedelta(weeks=2)),
    ('lisa', 'DIY Treehouse Build in My Backyard',
     'Built an entire treehouse from scratch. Here\'s the full build process.',
     620, now - timedelta(weeks=3)),
    ('kevin', 'Sunset Kayaking with Friends - Best Day Ever',
     'Beautiful sunset kayaking session. The views were absolutely incredible.',
     5200, now - timedelta(days=30)),
    ('emma', 'My Cat Learned a New Trick (You Won\'t Believe It)',
     'Mr. Whiskers can now open doors. I caught it all on camera!',
     12000, now - timedelta(days=4)),
    ('nina', 'Study With Me - Cozy Library Ambience',
     '2 hour study session with relaxing library sounds. Perfect for focus.',
     8900, now - timedelta(days=2)),
    ('maria', 'Baking a Birthday Cake for My Best Friend',
     'Attempted to bake the most beautiful cake for my bestie\'s birthday.',
     1800, now - timedelta(weeks=1)),
    ('maria', 'My Morning Routine - Realistic Edition',
     'No filters, no pretending - this is what my mornings actually look like.',
     760, now - timedelta(weeks=2)),
    ('maria', 'First Time Camping Solo - Was It Worth It?',
     'I went camping alone for the first time. Here\'s how it went.',
     4100, now - timedelta(days=30)),
]

for username, title, desc, views, date in videos_data:
    Video.objects.get_or_create(
        title=title,
        defaults={
            'description': desc,
            'file': 'videos/sample.mp4',
            'author': users[username],
            'views': views,
            'visibility': 'public',
            'created_at': date,
        }
    )

# Some dummy comments just to showcase.
video1 = Video.objects.filter(title__icontains='Zoo').first()
if video1 and video1.comments.count() == 0:
    Comment.objects.create(
        video=video1, author=users['jake'],
        text='The giraffe part was so cute! What zoo was this? Need to take my family there.',
        created_at=now - timedelta(days=2)
    )
    Comment.objects.create(
        video=video1, author=users['sarah'],
        text="Your kids' reactions to the penguins had me smiling the whole time haha",
        created_at=now - timedelta(days=1)
    )
    Comment.objects.create(
        video=video1, author=users['tom'],
        text='Great vlog! The sea lion show looked amazing. More zoo content please!',
        created_at=now - timedelta(hours=12)
    )

# Create some subscriptions
Subscription.objects.get_or_create(subscriber=users['jake'], channel=users['maria'])
Subscription.objects.get_or_create(subscriber=users['sarah'], channel=users['maria'])
Subscription.objects.get_or_create(subscriber=users['tom'], channel=users['maria'])
Subscription.objects.get_or_create(subscriber=users['emma'], channel=users['maria'])

print(f'Seeded {Video.objects.count()} videos, {Comment.objects.count()} comments, {User.objects.count()} users')
