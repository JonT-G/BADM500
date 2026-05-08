"""
Module handles incoming HTTP requests to the Actors inbox, verifies their signatures, parses the activity, 
and does actions such as creating RemoteFollower entries for Follow activities.
Returns a Django HttpResponse so the calling view can just return it.
"""

import json
import logging

from django.contrib.auth.models import User
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)

from .actor import actor_url
from .delivery import DeliveryError, deliver_activity
from .http_signatures import parse_signature_header, verify_request
from .models import RemoteFollower
from .remote import RemoteFetchError, fetch_public_key_pem


logger = logging.getLogger(__name__)


def handle_inbox_post(local_user: User, request: HttpRequest) -> HttpResponse:
    """
    Handle an incoming POST to a local Actor's inbox. This is the main entry point for processing all incoming activities.
    """
    sig_header = request.headers.get('Signature')
    if not sig_header:
        return HttpResponseBadRequest("missing Signature header")

    parsed_sig = parse_signature_header(sig_header)
    key_id = parsed_sig.get('keyId')
    if not key_id:
        return HttpResponseBadRequest("Signature header missing keyId")

    try:
        public_key_pem, remote_actor = fetch_public_key_pem(key_id)
    except RemoteFetchError as exc:
        logger.warning("Failed to fetch remote key for %s: %s", key_id, exc)
        return HttpResponseForbidden("could not fetch remote actor")

    body = request.body
    headers = dict(request.headers)
    # Host is a required header for signature verification, 
    # but Django does not include it in request.headers, so we add it back.
    headers.setdefault('Host', request.get_host())
    signature_ok = verify_request(
        method=request.method,
        path=request.get_full_path(),
        headers=headers,
        body=body,
        public_key_pem=public_key_pem,
    )
    if not signature_ok:
        return HttpResponseForbidden("invalid HTTP Signature")

    try:
        activity = json.loads(body)
    except ValueError:
        return HttpResponseBadRequest("invalid JSON body")

    activity_type = activity.get('type')
    if activity_type == 'Follow':
        return _handle_follow(local_user, activity, remote_actor)
    if activity_type == 'Undo':
        return _handle_undo(local_user, activity, remote_actor)

    # Unsupported activity types are not an error so just ignore them and return 202 Accepted. 
    logger.info("Ignoring unsupported activity type: %s", activity_type)
    return HttpResponse(status=202)


def _handle_follow(local_user: User, follow_activity: dict, remote_actor: dict) -> HttpResponse:
    """
    Handle an incoming Follow activity by creating/updating a RemoteFollower and sending back an Accept.
    The Follows actor must match the signing actor, and the Follow's object must point at this local user, 
    if not then it might be a false Follow. 
    """
    follower_uri = follow_activity.get('actor')
    object_uri = follow_activity.get('object')
    if not follower_uri or not object_uri:
        return HttpResponseBadRequest("Follow missing actor or object")
    
    expected_object = actor_url(local_user.username)
    if object_uri != expected_object:
        return HttpResponseBadRequest(
            f"Follow.object {object_uri} does not match this actor"
        )
    if remote_actor.get('id') != follower_uri:
        return HttpResponseBadRequest("Follow.actor does not match signing actor")

    inbox_uri = remote_actor.get('inbox')
    public_key_pem = (remote_actor.get('publicKey') or {}).get('publicKeyPem', '')
    if not inbox_uri or not public_key_pem:
        return HttpResponseBadRequest("remote actor missing inbox or publicKey")

    follower, _created = RemoteFollower.objects.update_or_create(
        target_user=local_user,
        actor_uri=follower_uri,
        defaults={
            'inbox_uri': inbox_uri,
            'public_key_pem': public_key_pem,
        },
    )

    accept = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"{actor_url(local_user.username)}#accepts/follows/{follower.pk}",
        "type": "Accept",
        "actor": actor_url(local_user.username),
        "object": follow_activity,
    }

    try:
        deliver_activity(accept, inbox_uri, local_user)
    except DeliveryError as exc:
        logger.error("Failed to deliver Accept to %s: %s", inbox_uri, exc)

    return HttpResponse(status=202)


def _handle_undo(local_user: User, undo_activity: dict, remote_actor: dict) -> HttpResponse:
    """Handle an incoming Undo activity. Currently only supports Undo of Follow"""
    inner = undo_activity.get('object')
    if not isinstance(inner, dict):
        return HttpResponseBadRequest("Undo.object must be the original activity object")
    inner_type = inner.get('type')
    if inner_type == 'Follow':
        return _handle_undo_follow(local_user, undo_activity, inner, remote_actor)
    logger.info("Ignoring Undo of unsupported type: %s", inner_type)
    return HttpResponse(status=202)


def _handle_undo_follow(
    local_user: User,
    undo_activity: dict,
    follow_object: dict,
    remote_actor: dict,
) -> HttpResponse:
    """
    Handle an Undo of a Follow by deleting the corresponding RemoteFollower.
    The Undo.actor, Undo.object.actor, and signing actor must all match to prevent abuse.
    """
    outer_actor = undo_activity.get('actor')
    inner_actor = follow_object.get('actor')
    if outer_actor != inner_actor:
        return HttpResponseBadRequest("Undo.actor and Undo.object.actor must match")
    if remote_actor.get('id') != outer_actor:
        return HttpResponseBadRequest("Undo.actor does not match signing actor")

    expected_object = actor_url(local_user.username)
    if follow_object.get('object') != expected_object:
        return HttpResponseBadRequest("Undo.object.object does not match this actor")

    RemoteFollower.objects.filter(
        target_user=local_user,
        actor_uri=outer_actor,
    ).delete()
    return HttpResponse(status=202)
