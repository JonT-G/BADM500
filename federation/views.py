"""
ActivityPub HTTP endpoints.

Module implements the endpoints required by the ActivityPub spec (https://www.w3.org/TR/activitypub/#endpoints) for Actors, Inbox, Outbox, Followers, and Following. It also implements the WebFinger endpoint (RFC 7033) for resolving user handles to Actor URLs.
- Actor URL: /users/<username>
- Inbox: /users/<username>/inbox
- Outbox: /users/<username>/outbox
- Followers: /users/<username>/followers
- Following: /users/<username>/following
- WebFinger: /.well-known/webfinger
"""

import json
from django.contrib.auth.models import User
from django.http import (HttpResponse, HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .actor import actor_url, build_actor
from .activities import build_create_video_activity
from .inbox import handle_inbox_post
from .models import RemoteFollower

ACTIVITY_JSON = "application/activity+json"
JRD_JSON = "application/jrd+json"


def _ap_response(payload, content_type=ACTIVITY_JSON, status=200):
    """Helper to return a JSON response with the right content type for ActivityPub or WebFinger"""
    return HttpResponse(
        json.dumps(payload, ensure_ascii=False),
        content_type=content_type,
        status=status,
    )


def _empty_collection(collection_id):
    """Helper to return an empty OrderedCollection with the given id. For collection not implemented like "following" or "likes"."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": collection_id,
        "type": "OrderedCollection",
        "totalItems": 0,
        "orderedItems": [],
    }


@require_GET
def actor(request, username):
    """Actor endpoint, returns the Actor JSON-LD document."""
    user = get_object_or_404(User, username=username)
    return _ap_response(build_actor(user))


@require_GET
def followers(request, username):
    """Followers endpoint, returns a list of follower Actor URLs."""
    user = get_object_or_404(User, username=username)
    follower_uris = list(
        RemoteFollower.objects.filter(target_user=user).values_list('actor_uri', flat=True)
    )
    payload = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"{actor_url(user.username)}/followers",
        "type": "OrderedCollection",
        "totalItems": len(follower_uris),
        "orderedItems": follower_uris,
    }
    return _ap_response(payload)


@require_GET
def following(request, username):
    """Following endpoint. Not implemented, returns an empty collection."""
    user = get_object_or_404(User, username=username)
    return _ap_response(_empty_collection(f"{actor_url(user.username)}/following"))


@require_GET
def outbox(request, username):
    """
    Outbox endpoint, returns a list of recent activities by this actor.
    All public videos is returned as Create activities. 
    """
    user = get_object_or_404(User, username=username)
    public_videos = user.videos.filter(visibility='public')
    items = [build_create_video_activity(v) for v in public_videos]
    payload = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"{actor_url(user.username)}/outbox",
        "type": "OrderedCollection",
        "totalItems": len(items),
        "orderedItems": items,
    }
    return _ap_response(payload)


@csrf_exempt
def inbox(request, username):
    """
Inbox endpoint, accepts incoming activities.
    """
    user = get_object_or_404(User, username=username)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    return handle_inbox_post(user, request)