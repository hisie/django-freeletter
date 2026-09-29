from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("newsletter/", include("freeletter.urls")),
]
