from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse

from freeletter.models import Issue, Subscriber
from freeletter.urls_helpers import absolute_url, absolutize_html


def _from_email() -> str:
    return getattr(settings, "FREELETTER_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)


def send_confirmation_email(subscriber: Subscriber, request: HttpRequest | None = None) -> None:
    confirm_url = absolute_url(
        reverse("freeletter:confirm", kwargs={"token": subscriber.confirmation_token}), request
    )
    context = {"subscriber": subscriber, "confirm_url": confirm_url}

    subject = render_to_string("freeletter/email/confirm_subject.txt", context).strip()
    text_body = render_to_string("freeletter/email/confirm.txt", context)

    message = EmailMultiAlternatives(
        subject, text_body, from_email=_from_email(), to=[subscriber.email]
    )
    message.send()


def send_issue_email(
    issue: Issue, subscriber: Subscriber, request: HttpRequest | None = None
) -> None:
    unsubscribe_url = absolute_url(
        reverse("freeletter:unsubscribe", kwargs={"token": subscriber.unsubscribe_token}), request
    )
    archive_url = absolute_url(issue.get_absolute_url(), request)
    context = {
        "issue": issue,
        "subscriber": subscriber,
        "unsubscribe_url": unsubscribe_url,
        "archive_url": archive_url,
        "blocks": [
            absolutize_html(block.render({"request": request}), request)
            for block in issue.blocks.all()
        ],
    }

    subject = issue.effective_subject()
    text_body = render_to_string("freeletter/email/issue.txt", context)
    html_body = render_to_string("freeletter/email/issue.html", context)

    message = EmailMultiAlternatives(
        subject, text_body, from_email=_from_email(), to=[subscriber.email]
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
