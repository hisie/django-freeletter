import pytest
from django.core import mail
from django.urls import reverse

from freeletter.models import Issue, IssueBlock, Subscriber

pytestmark = pytest.mark.django_db


def test_subscribe_creates_unconfirmed_subscriber_and_sends_confirmation(client):
    response = client.post(reverse("freeletter:subscribe"), {"email": "a@example.com", "name": "A"})

    assert response.status_code == 302
    subscriber = Subscriber.objects.get(email="a@example.com")
    assert not subscriber.is_confirmed
    assert len(mail.outbox) == 1
    assert subscriber.confirmation_token in mail.outbox[0].body


def test_confirm_link_activates_subscriber(client):
    subscriber = Subscriber.objects.create(email="a@example.com")

    response = client.get(
        reverse("freeletter:confirm", kwargs={"token": subscriber.confirmation_token})
    )

    assert response.status_code == 302
    subscriber.refresh_from_db()
    assert subscriber.is_confirmed


def test_unsubscribe_link_deactivates_subscriber(client):
    subscriber = Subscriber.objects.create(email="a@example.com", is_confirmed=True)

    response = client.get(
        reverse("freeletter:unsubscribe", kwargs={"token": subscriber.unsubscribe_token})
    )

    assert response.status_code == 302
    subscriber.refresh_from_db()
    assert not subscriber.is_active


def test_resubscribing_after_unsubscribe_resets_confirmation(client):
    subscriber = Subscriber.objects.create(
        email="a@example.com", is_confirmed=True, unsubscribed_at="2026-01-01T00:00:00Z"
    )

    client.post(reverse("freeletter:subscribe"), {"email": "a@example.com", "name": ""})

    subscriber.refresh_from_db()
    assert not subscriber.is_confirmed
    assert subscriber.unsubscribed_at is None
    assert len(mail.outbox) == 1


def test_already_active_subscriber_resubscribing_gets_no_new_email(client):
    Subscriber.objects.create(email="a@example.com", is_confirmed=True)

    client.post(reverse("freeletter:subscribe"), {"email": "a@example.com", "name": ""})

    assert len(mail.outbox) == 0


def test_archive_only_lists_sent_issues(client):
    Issue.objects.create(title="Draft one", slug="draft-one", status=Issue.Status.DRAFT)
    sent = Issue.objects.create(title="Sent one", slug="sent-one", status=Issue.Status.SENT)

    response = client.get(reverse("freeletter:issue-list"))

    titles = [issue.title for issue in response.context["issues"]]
    assert titles == [sent.title]


def test_draft_issue_detail_is_not_reachable(client):
    Issue.objects.create(title="Draft one", slug="draft-one", status=Issue.Status.DRAFT)

    response = client.get(reverse("freeletter:issue-detail", kwargs={"slug": "draft-one"}))

    assert response.status_code == 404


def test_sent_issue_detail_renders_its_blocks(client):
    issue = Issue.objects.create(title="Sent one", slug="sent-one", status=Issue.Status.SENT)
    IssueBlock.objects.create(issue=issue, block_type="html", html="<p>Hello world</p>")

    response = client.get(issue.get_absolute_url())

    assert response.status_code == 200
    assert "Hello world" in response.content.decode()
