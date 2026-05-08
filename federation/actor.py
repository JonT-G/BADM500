"""
Build ActivityPub Actor JSON-LD documents.
Builds the Actor metadata for our local users, which is served by the view in federation/views.py.
"""

from django.conf import settings
from django.urls import reverse


def actor_url(username):
    """Actor id URL for a given username"""
    return f"{settings.SITE_URL}{reverse('federation:actor', args=[username])}"


def build_actor(user):
    """
    Return the JSON-LD dict for a local user's Actor document.
    """
    base = actor_url(user.username)
    profile = user.profile

    actor = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
        ],
        "id": base,
        "type": "Person",
        "preferredUsername": user.username,
        "name": user.username,
        "summary": profile.bio or "",
        "inbox": f"{base}/inbox",
        "outbox": f"{base}/outbox",
        "followers": f"{base}/followers",
        "following": f"{base}/following",
        "publicKey": {
            "id": f"{base}#main-key",
            "owner": base,
            "publicKeyPem": profile.public_key,
        },
    }
    if profile.avatar:
        actor["icon"] = {
            "type": "Image",
            "url": f"{settings.SITE_URL}{profile.avatar.url}",
        }
    return actor
