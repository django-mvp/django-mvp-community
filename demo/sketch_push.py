"""Stand-ins for web push while its screens are sketched. Nothing here sends a push.

The push channel is registered so the preferences page draws its column. The
push subscriptions are kept in the session, so turning push on and stopping a
browser change what the page lists. The state of the browser in use is read
from ``?sketch_browser=``, because a browser on the development server, which is
served over plain HTTP, has no push support to detect.
"""

from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from generic_notifications.channels import BaseChannel
from generic_notifications.registry import registry

BROWSER_STATES = ("offer", "on", "denied", "unsupported", "homescreen")

SEEDS = {
    "none": [],
    "few": [
        {"id": 2, "name": "Safari on iPhone", "kind": "phone", "turned_on": "2026-10-02"},
        {"id": 3, "name": "Chrome on Android", "kind": "phone", "turned_on": "2026-08-14"},
    ],
    "many": [
        {"id": 2, "name": "Safari on iPhone", "kind": "phone", "turned_on": "2026-10-02"},
        {"id": 3, "name": "Chrome on Android", "kind": "phone", "turned_on": "2026-08-14"},
        {"id": 4, "name": "Firefox on Windows", "kind": "computer", "turned_on": "2026-07-30"},
        {"id": 5, "name": "Microsoft Edge on Windows", "kind": "computer", "turned_on": "2026-06-11"},
        {"id": 6, "name": "Safari on iPad", "kind": "tablet", "turned_on": "2026-05-02"},
        {"id": 7, "name": "Samsung Internet on Android", "kind": "phone", "turned_on": "2026-03-19"},
        {"id": 8, "name": "Firefox on Linux", "kind": "computer", "turned_on": "2026-01-08"},
        {"id": 9, "name": "Chrome on macOS", "kind": "computer", "turned_on": "2025-11-23"},
    ],
}

THIS_BROWSER = {"id": 1, "name": "Firefox on Windows", "kind": "computer", "current": True}


class SketchPushChannel(BaseChannel):
    """Draws the push column on the preferences page and sends nothing."""

    key = "push"
    name = "Push"

    def send_now(self, notification):
        """Send nothing: the sketch has no push service."""


registry.register_channel(SketchPushChannel, force=True)


def subscriptions(request):
    """The signed-in person's stand-in push subscriptions, seeded on first use."""
    seed = request.GET.get("sketch_devices")
    if seed in SEEDS:
        request.session["sketch_push"] = [dict(row) for row in SEEDS[seed]]
    if "sketch_push" not in request.session:
        request.session["sketch_push"] = [dict(row) for row in SEEDS["few"]]
    return request.session["sketch_push"]


def push(request):
    """Give the preferences page the stand-in push state.

    Args:
        request: The current request.

    Returns:
        ``push`` for the preferences page, and nothing anywhere else.
    """
    if not request.user.is_authenticated:
        return {}
    if request.path != reverse("mvp_community_notifications:preferences"):
        return {}
    rows = subscriptions(request)
    state = request.GET.get("sketch_browser")
    if state in BROWSER_STATES:
        request.session["sketch_browser"] = state
        if state == "on" and not any(row.get("current") for row in rows):
            rows.insert(0, {**THIS_BROWSER, "turned_on": date.today().isoformat()})
        if state != "on":
            rows[:] = [row for row in rows if not row.get("current")]
        request.session.modified = True
    state = request.session.get("sketch_browser", "offer")
    shown = [{**row, "turned_on": date.fromisoformat(row["turned_on"])} for row in rows]
    return {
        "push": {
            "browser": state,
            "just_turned_on": request.session.pop("sketch_push_just_on", False),
            "subscriptions": shown,
        }
    }


class TurnOnView(LoginRequiredMixin, View):
    """Store this browser as a push subscription, as the real view will after the browser allows it."""

    def post(self, request):
        """Add this browser, mark the test push as sent, and go back to the page."""
        rows = subscriptions(request)
        if not any(row.get("current") for row in rows):
            rows.insert(0, {**THIS_BROWSER, "turned_on": date.today().isoformat()})
        request.session["sketch_browser"] = "on"
        request.session["sketch_push_just_on"] = True
        request.session.modified = True
        return redirect("mvp_community_notifications:preferences")


class StopView(LoginRequiredMixin, View):
    """Stop push to one of the person's browsers."""

    def post(self, request, pk):
        """Remove the browser, say so, and go back to the page."""
        rows = subscriptions(request)
        stopped = next((row for row in rows if row["id"] == pk), None)
        if stopped:
            rows.remove(stopped)
            if stopped.get("current"):
                request.session["sketch_browser"] = "offer"
            request.session.modified = True
            messages.success(request, f"Push to {stopped['name']} is stopped.")
        return redirect("mvp_community_notifications:preferences")
