"""URL routes for the demo project."""

from django.contrib import admin
from django.urls import include, path

from demo.views import (
    GroupActivityView,
    GroupView,
    OverviewView,
    PeopleView,
    PersonView,
    SendNotificationView,
)
from mvp_community.integrations.activity.views import ActivityFeedView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", OverviewView.as_view(), name="overview"),
    path(
        "send-notification/",
        SendNotificationView.as_view(),
        name="send_notification",
    ),
    path("people/", PeopleView.as_view(), name="people"),
    path("people/<int:pk>/", PersonView.as_view(), name="person"),
    path("groups/<int:pk>/", GroupView.as_view(), name="group"),
    # A feed is a view the host project mounts: what the signed-in person
    # follows, the whole site's, and one group's.
    path(
        "activity/",
        ActivityFeedView.as_view(
            page_title="Your feed",
            page_lead="What the people and things you follow have been doing.",
            breadcrumbs=[{"text": "Your feed"}],
        ),
        name="feed",
    ),
    path(
        "activity/site/",
        ActivityFeedView.as_view(
            stream="site",
            page_lead="Everything that has happened on the site.",
            breadcrumbs=[{"text": "Site activity"}],
        ),
        name="site_activity",
    ),
    path(
        "groups/<int:pk>/activity/",
        GroupActivityView.as_view(),
        name="group_activity",
    ),
    path("", include("mvp_community.integrations.notifications.urls")),
    path("", include("mvp_community.integrations.activity.urls")),
    path("", include("mvp_community.integrations.push.urls")),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
