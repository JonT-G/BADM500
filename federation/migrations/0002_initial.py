"""
this migration creates the RemoteFollower model, which tracks remote followers of local users.
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('federation', '0001_backfill_actor_keypairs'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteFollower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor_uri', models.URLField(max_length=500)),
                ('inbox_uri', models.URLField(max_length=500)),
                ('public_key_pem', models.TextField()),
                ('accepted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('target_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remote_followers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-accepted_at'],
                'unique_together': {('target_user', 'actor_uri')},
            },
        ),
    ]
