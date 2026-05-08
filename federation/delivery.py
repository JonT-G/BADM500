"""
Outbound activity delivery.

Posts a signed ActivityPub activity (Accept, Create, ...) to a remote inbox.
Synchronous HTTP delivery. In real production use asynchronous delivery. 
"""

import json
import logging

import requests

from .actor import actor_url
from .http_signatures import sign_request_headers


ACTIVITY_JSON = "application/activity+json"
USER_AGENT = "BADM500-Federation/0.1 (+https://github.com/JonT-G/BADM500)"

logger = logging.getLogger(__name__)


class DeliveryError(Exception):
    """Remote server rejected delivery."""


def deliver_activity(activity: dict, target_inbox_uri: str, sender_user, timeout: float = 10.0) -> int:
    """
    POST activity to target_inbox_uri, signed by sender_user.
    Returns the HTTP status code on success. Raises DeliveryError on failure.
    """
    body = json.dumps(activity, ensure_ascii=False).encode('utf-8')
    key_id = f"{actor_url(sender_user.username)}#main-key"
    private_key_pem = sender_user.profile.private_key

    signed_headers = sign_request_headers(
        method='POST',
        url=target_inbox_uri,
        body=body,
        key_id=key_id,
        private_key_pem=private_key_pem,
    )
    headers = {
        'Content-Type': ACTIVITY_JSON,
        'Accept': ACTIVITY_JSON,
        'User-Agent': USER_AGENT,
        **signed_headers,
    }

    try:
        response = requests.post(target_inbox_uri, data=body, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise DeliveryError(f"POST {target_inbox_uri} failed: {exc}") from exc

    if response.status_code >= 300:
        logger.warning(
            "Delivery to %s rejected: %s %s",
            target_inbox_uri, response.status_code, response.text[:200],
        )
        raise DeliveryError(
            f"POST {target_inbox_uri} returned {response.status_code}: {response.text[:200]}"
        )
    return response.status_code


def deliver_to_followers(activity: dict, sender_user) -> dict:
    """
    Fan out an activity to every RemoteFollower of `sender_user`.
    Returns a {inbox_uri: status_or_error} dict. One failed delivery does
    not abort the rest of the deliveries, but all errors are collected and returned in the dict. 
    """
    from .models import RemoteFollower

    results: dict = {}
    followers = RemoteFollower.objects.filter(target_user=sender_user)
    for follower in followers:
        try:
            results[follower.inbox_uri] = deliver_activity(
                activity, follower.inbox_uri, sender_user,
            )
        except DeliveryError as exc:
            logger.error("Delivery to %s failed: %s", follower.inbox_uri, exc)
            results[follower.inbox_uri] = f"error: {exc}"
    return results
