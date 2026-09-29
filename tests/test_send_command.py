import pytest
from django.core import mail
from django.core.management import call_command

from freeletter.models import Issue, IssueBlock, Subscriber

pytestmark = pytest.mark.django_db


def test_send_command_only_reaches_active_subscribers_and_marks_issue_sent():
    issue = Issue.objects.create(
        title="Autumn sale", slug="autumn-sale", status=Issue.Status.QUEUED
    )
    IssueBlock.objects.create(issue=issue, block_type="html", html="<p>Save 20%</p>")

    active = Subscriber.objects.create(email="active@example.com", is_confirmed=True)
    Subscriber.objects.create(email="unconfirmed@example.com", is_confirmed=False)
    Subscriber.objects.create(
        email="unsubscribed@example.com", is_confirmed=True, unsubscribed_at="2026-01-01T00:00:00Z"
    )

    call_command("send_freeletter_issues")

    issue.refresh_from_db()
    assert issue.status == Issue.Status.SENT
    assert issue.sent_at is not None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [active.email]
    assert mail.outbox[0].subject == "Autumn sale"


def test_send_command_ignores_draft_issues():
    Issue.objects.create(title="Not ready", slug="not-ready", status=Issue.Status.DRAFT)
    Subscriber.objects.create(email="a@example.com", is_confirmed=True)

    call_command("send_freeletter_issues")

    assert len(mail.outbox) == 0


def test_send_command_continues_past_a_single_recipient_failure(monkeypatch):
    issue = Issue.objects.create(title="Issue", slug="issue", status=Issue.Status.QUEUED)
    IssueBlock.objects.create(issue=issue, block_type="html", html="<p>Hi</p>")
    Subscriber.objects.create(email="bad@example.com", is_confirmed=True)
    good = Subscriber.objects.create(email="good@example.com", is_confirmed=True)

    import freeletter.management.commands.send_freeletter_issues as cmd_module

    original = cmd_module.send_issue_email

    def flaky(issue_, subscriber, request=None):
        if subscriber.email == "bad@example.com":
            raise RuntimeError("SMTP exploded")
        return original(issue_, subscriber, request)

    monkeypatch.setattr(cmd_module, "send_issue_email", flaky)

    call_command("send_freeletter_issues")

    issue.refresh_from_db()
    assert issue.status == Issue.Status.SENT
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [good.email]
