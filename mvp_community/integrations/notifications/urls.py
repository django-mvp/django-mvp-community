"""The notifications extra's pages. A project includes these where it wants them."""

from django.urls import path

from . import views

app_name = "mvp_community_notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("read/", views.MarkAllReadView.as_view(), name="mark_all_read"),
    path("<int:pk>/", views.OpenNotificationView.as_view(), name="open"),
    path("bell/", views.BellView.as_view(), name="bell"),
    path("preferences/", views.PreferencesView.as_view(), name="preferences"),
]
