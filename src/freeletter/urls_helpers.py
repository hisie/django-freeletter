"""Absolute-URL building for email content — a view has a request to build
one from, a management command sending a queued issue doesn't, so this
covers both."""

from __future__ import annotations

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
