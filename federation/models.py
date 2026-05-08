"""Federation-specific models.

Module for models related to federation features, such as tracking remote followers.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class RemoteFollower(models.Model):
    """
    Represents a remote follower of a local user. Stores the follower's actor URI, inbox URI, and public key for signature verification.
    When we receive a Follow activity from a remote server, we create a RemoteFollower for that user. 
    If we receive an Undo of that Follow, we delete the RemoteFollower.
    """
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='remote_followers',
    )
    actor_uri = models.URLField(max_length=500)
    inbox_uri = models.URLField(max_length=500)
    public_key_pem = models.TextField()
    accepted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('target_user', 'actor_uri')
        ordering = ['-accepted_at']

    def __str__(self):
        return f'{self.actor_uri} -> {self.target_user.username}'
