"""Absolute-URL building for email content — a view has a request to build
one from, a management command sending a queued issue doesn't, so this
covers both."""

from __future__ import annotations

import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest


def absolute_url(path: str, request: HttpRequest | None = None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)

    base_url = getattr(settings, "FREELETTER_BASE_URL", None)
    if not base_url:
        raise ImproperlyConfigured(
            "FREELETTER_BASE_URL must be set to build links in emails sent "
            "outside of a request (e.g. from the send_freeletter_issues "
            "management command)."
        )
    return base_url.rstrip("/") + path


_RELATIVE_URL_ATTR = re.compile(r"""(\b(?:src|href)\s*=\s*)(["'])/(?!/)""", re.IGNORECASE)


def absolutize_html(html: str, request: HttpRequest | None = None) -> str:
    """Turn root-relative `src`/`href` URLs (`/media/x.jpg`) into absolute ones.

    An email is read in a client that knows nothing about the site's domain,
    so a relative image or link resolves to nothing. Block templates emit
    `image.url` / `get_absolute_url` as-is; this fixes them in one place.
    Protocol-relative (`//host/x`), already-absolute and `cid:`/`data:` URLs
    are left alone."""
    root = absolute_url("/", request)

    def _replace(match: re.Match) -> str:
        return f"{match.group(1)}{match.group(2)}{root}"

    return _RELATIVE_URL_ATTR.sub(_replace, html)
