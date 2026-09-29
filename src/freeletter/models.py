import secrets

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _token() -> str:
    return secrets.token_urlsafe(32)


class Subscriber(models.Model):
    email = models.EmailField(_("email"), unique=True)
    name = models.CharField(_("name"), max_length=200, blank=True)

    is_confirmed = models.BooleanField(_("confirmed"), default=False)
    confirmation_token = models.CharField(
        max_length=64, unique=True, default=_token, editable=False
    )
    unsubscribe_token = models.CharField(max_length=64, unique=True, default=_token, editable=False)

    subscribed_at = models.DateTimeField(_("subscribed at"), auto_now_add=True)
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)
    unsubscribed_at = models.DateTimeField(_("unsubscribed at"), null=True, blank=True)

    class Meta:
        ordering = ("-subscribed_at",)
        verbose_name = _("subscriber")
        verbose_name_plural = _("subscribers")

    def __str__(self) -> str:
        return self.email

    @property
    def is_active(self) -> bool:
        """Confirmed and not (yet) unsubscribed — the only subscribers an
        issue send actually reaches."""
        return self.is_confirmed and self.unsubscribed_at is None

    def confirm(self) -> None:
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])

    def unsubscribe(self) -> None:
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["unsubscribed_at"])


class Issue(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        QUEUED = "queued", _("Queued")
        SENT = "sent", _("Sent")

    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    subject = models.CharField(
        _("email subject"),
        max_length=255,
        blank=True,
        help_text=_("Defaults to the title if left blank."),
    )

    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    queued_at = models.DateTimeField(_("queued at"), null=True, blank=True)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)

    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("date updated"), auto_now=True)

    class Meta:
        ordering = ("-date_created",)
        verbose_name = _("issue")
        verbose_name_plural = _("issues")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("freeletter:issue-detail", kwargs={"slug": self.slug})

    def effective_subject(self) -> str:
        return self.subject or self.title

    def queue(self) -> None:
        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        self.save(update_fields=["status", "queued_at"])


class IssueBlock(models.Model):
    """One block within an Issue. block_type "html" is core/built-in;
    anything else is resolved via freeletter.blocks' registry, with
    content_object as the block's payload (e.g. a blog post, a product) —
    see blocks.py's module docstring for why this stays generic here."""

    issue = models.ForeignKey(
        Issue, verbose_name=_("issue"), related_name="blocks", on_delete=models.CASCADE
    )
    sortorder = models.PositiveIntegerField(_("sort order"), default=0)
    block_type = models.CharField(_("block type"), max_length=50, default="html")

    # "html" block fields — meaningless for any other block_type.
    html = models.TextField(_("content"), blank=True)
    image = models.ImageField(_("image"), upload_to="freeletter/blocks/%Y/%m/%d/", blank=True)

    # Generic payload for a non-"html" block type.
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("content type"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    object_id = models.PositiveIntegerField(_("object id"), null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ("sortorder", "id")
        verbose_name = _("issue block")
        verbose_name_plural = _("issue blocks")

    def __str__(self) -> str:
        return f"{self.block_type} block on {self.issue}"

    def render(self, context: dict | None = None) -> str:
        from freeletter.blocks import get_block_type

        return get_block_type(self.block_type).render(self, context or {})
