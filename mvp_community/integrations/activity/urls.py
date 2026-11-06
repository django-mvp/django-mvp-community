"""The activity extra's routes.

Include this at the root, ``path("", include(...))``, as django-mvp's own URLs
are: each route chooses its own address.

Only django-activity-stream's four follow routes are taken from its URLconf.
The rest of it also shows actions that are not public and lists anyone's
follows to anyone. The follow routes keep their own names, with no namespace,
because django-activity-stream's template tags reverse them by those names.
"""

from actstream import urls as actstream_urls
from django.urls import include, path

from . import views

FOLLOW_ROUTES = {
    "actstream_follow",
    "actstream_follow_all",
    "actstream_unfollow",
    "actstream_unfollow_all",
}

pages = [
    path(
        "account-center/following/",
        views.FollowingView.as_view(),
        name="following",
    ),
]

follow_routes = [
    route
    for route in actstream_urls.urlpatterns
    if getattr(route, "name", None) in FOLLOW_ROUTES
]

urlpatterns = [
    path("", include((pages, "mvp_community_activity"))),
    path("activity/", include(follow_routes)),
]
