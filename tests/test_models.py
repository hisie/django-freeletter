import pytest

from freeletter.blocks import BlockType, get_block_type, is_registered, register_block_type
from freeletter.models import Issue, IssueBlock, Subscriber

pytestmark = pytest.mark.django_db


def test_subscriber_is_active_only_once_confirmed_and_not_unsubscribed():
    subscriber = Subscriber.objects.create(email="a@example.com")
    assert not subscriber.is_active

    subscriber.confirm()
    assert subscriber.is_active
    assert subscriber.confirmed_at is not None

    subscriber.unsubscribe()
    assert not subscriber.is_active
    assert subscriber.unsubscribed_at is not None


def test_subscriber_tokens_are_unique_and_not_email():
    a = Subscriber.objects.create(email="a@example.com")
    b = Subscriber.objects.create(email="b@example.com")
    assert a.confirmation_token != b.confirmation_token
    assert a.unsubscribe_token != a.confirmation_token


def test_issue_effective_subject_falls_back_to_title():
    issue = Issue.objects.create(title="Autumn sale", slug="autumn-sale")
    assert issue.effective_subject() == "Autumn sale"

    issue.subject = "Custom subject line"
    assert issue.effective_subject() == "Custom subject line"


def test_html_block_is_registered_by_the_app_itself():
    assert is_registered("html")
    block_type = get_block_type("html")
    assert block_type.requires_object is False


def test_html_block_renders_its_content():
    issue = Issue.objects.create(title="Issue", slug="issue")
    block = IssueBlock.objects.create(issue=issue, block_type="html", html="<p>Hello</p>")
    assert "<p>Hello</p>" in block.render()


def test_custom_block_type_can_be_registered_and_resolves_content_object():
    register_block_type(
        BlockType(slug="test-echo", label="Echo", template_name="freeletter_test/echo_block.html")
    )
    issue = Issue.objects.create(title="Issue", slug="issue-2")
    subscriber = Subscriber.objects.create(email="echoed@example.com")
    block = IssueBlock.objects.create(
        issue=issue, block_type="test-echo", content_object=subscriber
    )
    assert block.content_object == subscriber
    assert "echoed@example.com" in block.render()
