"""
Fetch remote ActivityPub Actor documents.

Module for fetching remote Actor metadata, primarily the public key needed for signature verification and the inbox URL needed for storing followers and delivering activities. 
This is used by federation/inbox.py when processing incoming activities, and also by federation/delivery.py when preparing outgoing activities to new recipients.
"""
import requests
from .http_signatures import key_id_to_actor_uri

ACTIVITY_JSON = "application/activity+json"
USER_AGENT = "BADM500-Federation/0.1 (+https://github.com/JonT-G/BADM500)"

class RemoteFetchError(Exception):
    """Error raised if fetching a remote Actor document or public key fails"""


def fetch_actor(actor_uri: str, timeout: float = 10.0) -> dict:
    """
    Fetch and return the Actor document at `actor_uri`. 
    Raises RemoteFetchError on failure."""
    try:
        response = requests.get(
            actor_uri,
            headers={'Accept': ACTIVITY_JSON, 'User-Agent': USER_AGENT},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise RemoteFetchError(f"GET {actor_uri} failed: {exc}") from exc

    if response.status_code != 200:
        raise RemoteFetchError(f"GET {actor_uri} returned {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise RemoteFetchError(f"GET {actor_uri} returned non-JSON: {exc}") from exc


def fetch_public_key_pem(key_id: str) -> tuple[str, dict]:
    """Resolve a Signature keyId to a (publicKeyPem, actor_doc) pair by fetching the remote Actor document. Raises RemoteFetchError on failure."""
    actor_uri = key_id_to_actor_uri(key_id)
    actor = fetch_actor(actor_uri)
    public_key = actor.get('publicKey') or {}
    pem = public_key.get('publicKeyPem')
    if not pem:
        raise RemoteFetchError(f"actor {actor_uri} has no publicKey.publicKeyPem")
    return pem, actor
