"""
Add private_key and public_key fields to Profile model for ActivityPub HTTP Signatures.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0004_video_duration_notification'),
    ]
    # Signal handler in federation/signals.py will generate keypairs if any profile does not have them.
    operations = [
        migrations.AddField(
            model_name='profile',
            name='private_key',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='profile',
            name='public_key',
            field=models.TextField(blank=True, default=''),
        ),
    ]
