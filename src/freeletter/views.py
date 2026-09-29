from __future__ import annotations

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView, RedirectView, TemplateView

from freeletter.emails import send_confirmation_email
from freeletter.forms import SubscribeForm
from freeletter.models import Issue, Subscriber


class SubscribeView(FormView):
    template_name = "freeletter/subscribe.html"
    form_class = SubscribeForm

    def get_success_url(self) -> str:
        return reverse("freeletter:subscribe-pending")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        name = form.cleaned_data["name"]

        subscriber, created = Subscriber.objects.get_or_create(email=email, defaults={"name": name})
        if not created and subscriber.is_active:
            # Already a live subscriber — nothing to do, don't re-send a
            # confirmation email or reset their history.
            return redirect(self.get_success_url())

        if not created:
            # Re-subscribing after unsubscribing, or a stale unconfirmed
            # signup: reset to a fresh pending-confirmation state.
            subscriber.name = name or subscriber.name
            subscriber.is_confirmed = False
            subscriber.confirmed_at = None
            subscriber.unsubscribed_at = None
            subscriber.save()

        send_confirmation_email(subscriber, self.request)
        return redirect(self.get_success_url())


class SubscribePendingView(TemplateView):
    template_name = "freeletter/subscribe_pending.html"


class ConfirmView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        subscriber = get_object_or_404(Subscriber, confirmation_token=kwargs["token"])
        subscriber.confirm()
        return reverse("freeletter:confirmed")


class ConfirmedView(TemplateView):
    template_name = "freeletter/confirmed.html"


class UnsubscribeView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        subscriber = get_object_or_404(Subscriber, unsubscribe_token=kwargs["token"])
        subscriber.unsubscribe()
        return reverse("freeletter:unsubscribed")


class UnsubscribedView(TemplateView):
    template_name = "freeletter/unsubscribed.html"


class SentIssueQuerysetMixin:
    def get_queryset(self):
        return Issue.objects.filter(status=Issue.Status.SENT)


class IssueListView(SentIssueQuerysetMixin, ListView):
    template_name = "freeletter/issue_list.html"
    context_object_name = "issues"
    paginate_by = 20


class IssueDetailView(SentIssueQuerysetMixin, DetailView):
    template_name = "freeletter/issue_detail.html"
    context_object_name = "issue"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blocks"] = [
            block.render({"request": self.request}) for block in self.object.blocks.all()
        ]
        return context
