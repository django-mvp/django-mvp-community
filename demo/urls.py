"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import GroupView, OverviewView, PeopleView, PersonView, SendNotificationView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path(
        "send-notification/",
        SendNotificationView.as_view(),
        name="send_notification",
    ),
    path("people/", PeopleView.as_view(), name="people"),
    path("people/<int:pk>/", PersonView.as_view(), name="person"),
    path("groups/<int:pk>/", GroupView.as_view(), name="group"),
    path("", include("mvp_community.integrations.notifications.urls")),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
