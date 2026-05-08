"""
Signal handlers that keep federation state in sync with core models.

Module is used for Django signals related to federation features, such as generating Actor keypairs for Profiles and announcing new public Videos to followers.
"""

import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .activities import build_create_video_activity
from .delivery import deliver_to_followers

from videos.models import Profile, Video

from .RSA import generate_actor_keypair


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Profile)
def ensure_actor_keypair(sender, instance, created, **kwargs):
    """
    Ensure that every Profile has an Actor keypair for signing activities.
    """
    if instance.public_key and instance.private_key:
        return
    private_pem, public_pem = generate_actor_keypair()
    Profile.objects.filter(pk=instance.pk).update(
        private_key=private_pem,
        public_key=public_pem,
    )
    # Update instance so if its a newly created profile, the keypair will be available immediately without needing to re-query.
    instance.private_key = private_pem
    instance.public_key = public_pem


@receiver(post_save, sender=Video)
def federate_new_video(sender, instance, created, **kwargs):
    """When a new public Video is created, announce it to followers with a Create activity"""
    if not created or instance.visibility != 'public':
        return

    def _deliver():
        activity = build_create_video_activity(instance)
        results = deliver_to_followers(activity, instance.author)
        if results:
            logger.info(
                "Federated video %s to %d follower(s): %s",
                instance.pk, len(results), results,
            )

    transaction.on_commit(_deliver)


@receiver(post_delete, sender=Video)
def federate_deleted_video(sender, instance, **kwargs):
    """When a public Video is deleted, announce it to followers with a Delete activity"""
    if instance.visibility != 'public':
        return

    from .activities import build_delete_video_activity
    from .delivery import deliver_to_followers

    activity = build_delete_video_activity(instance)
    author = instance.author  # needed for to able to deliver to followers, so we have to get it before the video is deleted.

    def _deliver():
        results = deliver_to_followers(activity, author)
        if results:
            logger.info(
                "Federated deletion of %s to %d follower(s): %s",
                activity['object'], len(results), results,
            )

    transaction.on_commit(_deliver)
