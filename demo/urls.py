"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    # django-mvp's Account Center, with a development sign-in and sign-out
    # until an account app such as allauth is installed.
    path("", include("mvp.urls")),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
