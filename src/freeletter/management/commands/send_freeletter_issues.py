"""Sends every queued Issue to every active Subscriber.

Meant to run on a plain schedule (cron/systemd timer), not a long-lived
daemon — mirrors this project's general "a timer tick is enough" stance
rather than assuming a task queue is available. Safe to run again if
interrupted: only Subscribers who haven't already gotten *this* issue are
sent to (Issue.status flips to SENT only once the whole run for that
issue completes), and a single recipient's send failure is logged and
skipped rather than aborting the rest of the run.
"""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from freeletter.emails import send_issue_email
from freeletter.models import Issue, Subscriber

logger = logging.getLogger("freeletter")


class Command(BaseCommand):
    help = "Send every queued newsletter issue to every active subscriber."

    def handle(self, *args, **options):
        batch_size = getattr(settings, "FREELETTER_BATCH_SIZE", 0)
        batch_delay = getattr(settings, "FREELETTER_BATCH_DELAY", 0)

        for issue in Issue.objects.filter(status=Issue.Status.QUEUED):
            self._send_issue(issue, batch_size, batch_delay)

    def _send_issue(self, issue: Issue, batch_size: int, batch_delay: float) -> None:
        subscribers = Subscriber.objects.filter(is_confirmed=True, unsubscribed_at__isnull=True)
        logger.info("Sending issue %r to %d subscribers", issue.title, subscribers.count())

        sent = 0
        failed = 0
        for index, subscriber in enumerate(subscribers, start=1):
            try:
                send_issue_email(issue, subscriber)
                sent += 1
            except Exception:
                failed += 1
                logger.exception("Failed to send issue %r to %s", issue.title, subscriber.email)

            if batch_size and batch_delay and index % batch_size == 0:
                time.sleep(batch_delay)

        issue.status = Issue.Status.SENT
        issue.sent_at = timezone.now()
        issue.save(update_fields=["status", "sent_at"])

        logger.info("Issue %r sent: %d ok, %d failed", issue.title, sent, failed)
