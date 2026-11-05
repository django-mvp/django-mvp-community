"""The activity extra's pages.

Include this at the root, ``path("", include(...))``, as django-mvp's own URLs
are, and django-activity-stream's own URLs under ``activity/``, which the follow
control posts to.
"""

from django.urls import include, path

from . import views

app_name = "mvp_community_activity"

urlpatterns = [
    path("activity/", views.FeedView.as_view(), name="feed"),
    path(
        "account-center/following/",
        views.FollowingView.as_view(),
        name="following",
    ),
]
