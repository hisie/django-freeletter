from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from freeletter.models import Issue, IssueBlock, Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_confirmed", "subscribed_at", "unsubscribed_at")
    list_filter = ("is_confirmed",)
    search_fields = ("email", "name")
    readonly_fields = (
        "confirmation_token",
        "unsubscribe_token",
        "subscribed_at",
        "confirmed_at",
        "unsubscribed_at",
    )


class IssueBlockInline(admin.TabularInline):
    model = IssueBlock
    extra = 1
    fields = ("sortorder", "block_type", "html", "image", "content_type", "object_id")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "queued_at", "sent_at")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [IssueBlockInline]
    actions = ["queue_for_sending"]

    @admin.action(description=_("Queue selected issues for sending"))
    def queue_for_sending(self, request, queryset):
        for issue in queryset.filter(status=Issue.Status.DRAFT):
            issue.queue()
