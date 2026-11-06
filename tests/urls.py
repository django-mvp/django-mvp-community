"""The suite's urlconf: the demo project's routes plus any test-only route."""

from django.urls import path

from demo.urls import urlpatterns as demo_urlpatterns
from mvp_community.integrations.activity.views import ActivityFeedView

urlpatterns = [
    *demo_urlpatterns,
    path(
        "test/finished-activity/",
        ActivityFeedView.as_view(stream="site", verb="finished"),
        name="finished_activity",
    ),
    path(
        "test/unconfigured-object-activity/",
        ActivityFeedView.as_view(stream="object"),
        name="unconfigured_object_activity",
    ),
    path(
        "test/unknown-stream-activity/",
        ActivityFeedView.as_view(stream="nobody"),
        name="unknown_stream_activity",
    ),
]
