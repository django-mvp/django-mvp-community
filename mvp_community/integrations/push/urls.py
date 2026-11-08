"""The push extra's routes.

Include this at the root, ``path("", include(...))``, as django-mvp's own URLs
are: each route chooses its own address.
"""

from django.urls import path

from . import views

app_name = "mvp_community_push"

urlpatterns = [
    path(
        "notifications/push/subscribe/", views.SubscribeView.as_view(), name="subscribe"
    ),
]
