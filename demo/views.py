"""The demo project's pages."""

# MVPTemplateView, not TemplateView: it supplies the page title, subtitle and
# breadcrumbs the application shell draws around the content.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from generic_notifications import send_notification
from mvp.views import MVPTemplateView

from demo.notifications import ReplyReceived


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
