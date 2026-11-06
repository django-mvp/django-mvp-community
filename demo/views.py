"""The demo project's pages."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from generic_notifications import send_notification

# MVPTemplateView, not TemplateView: it supplies the page title, subtitle and
# breadcrumbs the application shell draws around the content.
from mvp.views import MVPTemplateView

from demo.notifications import ReplyReceived
from mvp_community.integrations.activity.views import ActivityFeedView


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]


class SendNotificationView(LoginRequiredMixin, View):
    """Send the signed-in person a notification, to watch the bell's count rise."""

    def post(self, request):
        """Send one reply notification and tell the bell to refresh."""
        send_notification(
            recipient=request.user,
            notification_type=ReplyReceived,
            subject="Anna replied to your question",
            text="“I had the same trouble with the dative. Try the second exercise first.”",
            url=reverse("overview"),
        )
        response = HttpResponse(status=204)
        response["HX-Trigger"] = "notifications:changed"
        return response


class PeopleView(MVPTemplateView):
    """Everyone and every group on the demo site, each with its follow control."""

    template_name = "demo/people.html"
    page_title = "People and groups"
    page_lead = "Follow someone or something to see what they do in your feed."
    breadcrumbs = [{"text": "People and groups"}]

    def get_context_data(self, **kwargs):
        """Add the people and the groups."""
        context = super().get_context_data(**kwargs)
        context["people"] = (
            get_user_model().objects.exclude(first_name="").order_by("first_name")
        )
        context["groups"] = Group.objects.order_by("name")
        return context


class PersonView(MVPTemplateView):
    """One person: their follow control, their followers and their activity."""

    template_name = "demo/followable.html"
    breadcrumbs = [{"text": "People and groups", "href": "/people/"}]

    def get_context_data(self, **kwargs):
        """Add the person, and name the page after them."""
        context = super().get_context_data(**kwargs)
        person = get_object_or_404(get_user_model(), pk=self.kwargs["pk"])
        context["object"] = person
        context["kind"] = "Person"
        return context

    def get_page_title(self):
        """Name the page after the person."""
        person = get_object_or_404(get_user_model(), pk=self.kwargs["pk"])
        return person.get_full_name() or str(person)


class GroupView(MVPTemplateView):
    """One group: its follow control, its followers and what happened in it."""

    template_name = "demo/followable.html"
    breadcrumbs = [{"text": "People and groups", "href": "/people/"}]

    def get_context_data(self, **kwargs):
        """Add the group."""
        context = super().get_context_data(**kwargs)
        context["object"] = get_object_or_404(Group, pk=self.kwargs["pk"])
        context["kind"] = "Group"
        return context

    def get_page_title(self):
        """Name the page after the group."""
        return get_object_or_404(Group, pk=self.kwargs["pk"]).name


class GroupActivityView(ActivityFeedView):
    """The public activity around one group."""

    stream = "object"
    page_lead = "Everything that happened in this group."

    def get_stream_object(self):
        """Return the group named in the address."""
        return get_object_or_404(Group, pk=self.kwargs["pk"])

    def get_page_title(self):
        """Name the page after the group."""
        return f"Activity in {self.get_stream_object().name}"
