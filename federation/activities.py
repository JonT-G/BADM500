"""Build ActivityPub activities and content objects from local models.

Activity Streams 2.0 vocabulary:
    - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-video
    - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-create
    - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-delete
"""

import mimetypes

from django.conf import settings
from django.utils import timezone

from .actor import actor_url


PUBLIC_AUDIENCE = "https://www.w3.org/ns/activitystreams#Public"


def video_object_id(video) -> str:
    """URI for the Video content object."""
    return f"{settings.SITE_URL}/videos/{video.pk}"


def create_activity_id(video) -> str:
    """URI for the Create activity."""
    return f"{settings.SITE_URL}/videos/{video.pk}/create"


def delete_activity_id(video) -> str:
    """URI for the Delete activity."""
    return f"{settings.SITE_URL}/videos/{video.pk}/delete"


def _media_type_for(file_field) -> str:
    """MIME type for a Django FileField, defaults to video/mp4."""
    if not file_field:
        return "video/mp4"
    guess, _ = mimetypes.guess_type(file_field.name)
    return guess or "video/mp4"


def build_video_object(video) -> dict:
    """
    Render a videos.Video as an Activity Streams Video object.
    So build a dict with all the info about the video and return it. 
    This is used in build_create_video_activity to create the "object" field of the Create activity
    """
    actor = actor_url(video.author.username)
    watch_url = f"{settings.SITE_URL}/watch/{video.pk}/"
    
    url_entries = [
        {"type": "Link", "mediaType": "text/html", "href": watch_url},
    ]
    if video.file and video.file.name:
        url_entries.append({
            "type": "Link",
            "mediaType": _media_type_for(video.file),
            "href": f"{settings.SITE_URL}{video.file.url}",
        })

    obj = {
        "id": video_object_id(video),
        "type": "Video",
        "attributedTo": actor,
        "name": video.title,
        "content": video.description or "",
        "url": url_entries,
        "published": video.created_at.isoformat(),
        "to": [PUBLIC_AUDIENCE],
        "cc": [f"{actor}/followers"],
    }
    if video.duration:
        obj["duration"] = f"PT{int(video.duration)}S"
    if video.thumbnail and video.thumbnail.name:
        obj["icon"] = {
            "type": "Image",
            "url": f"{settings.SITE_URL}{video.thumbnail.url}",
        }
    return obj



def build_create_video_activity(video) -> dict:
    """Wrap a Video object in a public Create activity addressed to followers"""
    actor = actor_url(video.author.username)
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": create_activity_id(video),
        "type": "Create",
        "actor": actor,
        "published": video.created_at.isoformat(),
        "to": [PUBLIC_AUDIENCE],
        "cc": [f"{actor}/followers"],
        "object": build_video_object(video),
    }


def build_delete_video_activity(video) -> dict:
    """
    Build a Delete activity that retracts a previously-published Video.
    may need to change to tombstone later if metadata for this is needed.
    """
    actor = actor_url(video.author.username)
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": delete_activity_id(video),
        "type": "Delete",
        "actor": actor,
        "published": timezone.now().isoformat(),
        "to": [PUBLIC_AUDIENCE],
        "cc": [f"{actor}/followers"],
        "object": video_object_id(video),
    }
