"""The notifications extra's pages.

Include this at the root, ``path("", include(...))``, as django-mvp's own URLs
are: each route chooses its own address. The notifications page and the bell
sit under ``notifications/``, and the preferences page, which belongs to the
Account Center, sits under ``account-center/``.
"""

from django.urls import path

from . import views

app_name = "mvp_community_notifications"

urlpatterns = [
    path("notifications/", views.NotificationListView.as_view(), name="list"),
    path("notifications/read/", views.MarkAllReadView.as_view(), name="mark_all_read"),
    path("notifications/<int:pk>/", views.OpenNotificationView.as_view(), name="open"),
    path("notifications/bell/", views.BellView.as_view(), name="bell"),
    path(
        "account-center/notifications/",
        views.PreferencesView.as_view(),
        name="preferences",
    ),
]
