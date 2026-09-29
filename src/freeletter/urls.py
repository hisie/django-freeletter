from __future__ import annotations

from django.urls import path

from freeletter import views

app_name = "freeletter"

urlpatterns = [
    path("", views.IssueListView.as_view(), name="issue-list"),
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),
    path("subscribe/pending/", views.SubscribePendingView.as_view(), name="subscribe-pending"),
    path("confirm/<str:token>/", views.ConfirmView.as_view(), name="confirm"),
    path("confirmed/", views.ConfirmedView.as_view(), name="confirmed"),
    path("unsubscribe/<str:token>/", views.UnsubscribeView.as_view(), name="unsubscribe"),
    path("unsubscribed/", views.UnsubscribedView.as_view(), name="unsubscribed"),
    path("<slug:slug>/", views.IssueDetailView.as_view(), name="issue-detail"),
]
