"""The notifications extra's pages.

Include this at the root, ``path("", include(...))``, as django-mvp's own URLs
are: each route chooses its own address.
"""

from django.urls import path

from . import views

app_name = "mvp_community_notifications"

urlpatterns = [
    path("notifications/", views.NotificationListView.as_view(), name="list"),
    path("notifications/read/", views.MarkAllReadView.as_view(), name="mark_all_read"),
]
