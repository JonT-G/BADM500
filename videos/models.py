"""
Database models for the BADM500 video-sharing platform.

Models
------
Video, Comment, Like, Subscription, CommentVote, Profile,
WatchHistory, WatchLater, Notification.
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Video(models.Model):
    """A user-uploaded video with title, description, and visibility."""

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    views = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text='Duration in seconds')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        """Number of likes on this video."""
        return self.likes.filter(is_like=True).count()

    @property
    def dislike_count(self):
        """Number of dislikes on this video."""
        return self.likes.filter(is_like=False).count()


class Comment(models.Model):
    """A text comment left on a video."""

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} on {self.video.title}'

    @property
    def upvote_count(self):
        return self.votes.filter(is_upvote=True).count()

    @property
    def downvote_count(self):
        return self.votes.filter(is_upvote=False).count()


class Like(models.Model):
    """A like or dislike on a video (one per user per video)."""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True)

    class Meta:
        unique_together = ('video', 'user')

    def __str__(self):
        action = 'liked' if self.is_like else 'disliked'
        return f'{self.user.username} {action} {self.video.title}'


class Subscription(models.Model):
    """A subscriber ↔ channel relationship between two users."""
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('subscriber', 'channel')

    def __str__(self):
        return f'{self.subscriber.username} -> {self.channel.username}'


class CommentVote(models.Model):
    """Upvote or downvote on a comment (one per user per comment)."""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    is_upvote = models.BooleanField(default=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        action = 'upvoted' if self.is_upvote else 'downvoted'
        return f'{self.user.username} {action} comment #{self.comment.pk}'


class Profile(models.Model):
    """Extended user profile with bio and avatar image."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} profile'


class WatchHistory(models.Model):
    """Records which videos a user has watched (most-recent first)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='history_entries')
    watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-watched_at']
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user.username} watched {self.video.title}'


class WatchLater(models.Model):
    """Videos a user has saved for later viewing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_later')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='saved_entries')
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-added_at']
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user.username} saved {self.video.title}'


class Notification(models.Model):
    """A notification triggered by user interactions (likes, comments, etc.)."""
    VERB_CHOICES = [
        ('liked', 'liked your video'),
        ('commented', 'commented on your video'),
        ('subscribed', 'subscribed to your channel'),
        ('upvoted', 'upvoted your comment'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='acted_notifications')
    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor.username} {self.verb} → {self.recipient.username}'

    @property
    def message(self):
        """Human-readable notification text (without actor name)."""
        verb_text = self.get_verb_display()
        if self.video and self.verb != 'subscribed':
            return f'{verb_text} "{self.video.title}"'
        return verb_text


# Auto-create a Profile whenever a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
