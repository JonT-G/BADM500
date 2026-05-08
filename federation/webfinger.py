"""
WebFinger (RFC 7033) — resolves acct:user@host to an Actor URL.
This is what lets Mastodon translate "@alice@yourhost" into the Actor URI.
"""
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .actor import actor_url

ACTIVITY_JSON = "application/activity+json"
JRD_JSON = "application/jrd+json"


@require_GET
def webfinger(request):
    resource = request.GET.get("resource", "")
    if not resource.startswith("acct:") or "@" not in resource:
        return HttpResponseBadRequest("resource must be of the form acct:user@host")

    handle = resource[len("acct:"):]
    username, _, host = handle.partition("@")
    expected_host = urlsplit(settings.SITE_URL).netloc
    if host != expected_host:
        return HttpResponse(status=404)

    user = get_object_or_404(User, username=username)
    payload = {"subject": f"acct:{user.username}@{expected_host}","links": [
            {
                "rel": "self",
                "type": ACTIVITY_JSON,
                "href": actor_url(user.username),
            },
        ],
    }
    return HttpResponse(
        __import__('json').dumps(payload),
        content_type=JRD_JSON,
    )