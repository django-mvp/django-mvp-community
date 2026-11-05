"""The notifications page, the bell's refresh and the preferences page."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from generic_notifications.models import Notification
from generic_notifications.preferences import get_notification_preferences
from generic_notifications.registry import registry
from generic_notifications.utils import get_notifications
from mvp.views import MVPListView, MVPTemplateView


class NotificationListView(LoginRequiredMixin, MVPListView):
    """A person's notifications on the site, newest first."""

    model = Notification
    template_name = "mvp_community/notifications/list.html"
    paginate_by = 20
    page_title = _("Notifications")
    breadcrumbs = [{"text": _("Notifications")}]

    def get_queryset(self):
        """Return the signed-in person's notifications that arrived on the site."""
        return get_notifications(self.request.user)


class MarkAllReadView(LoginRequiredMixin, View):
    """Mark every unread notification the person sees on the site as read."""

    http_method_names = ["post", "options"]

    def post(self, request):
        """Mark them read and go back to the list.

        Only notifications on the site are touched. ``mark_notifications_as_read``
        also marks the ones sent only by email, which would stop their digest.

        Args:
            request: The POST request.

        Returns:
            A redirect to the notifications page.
        """
        get_notifications(request.user, unread_only=True).update(read=timezone.now())
        return redirect("mvp_community_notifications:list")


class OpenNotificationView(LoginRequiredMixin, View):
    """Mark one of the person's notifications read and follow its link."""

    def get(self, request, pk):
        """Mark it read, then go to where it points.

        Args:
            request: The GET request.
            pk: The notification's primary key. Another person's is a 404.

        Returns:
            A redirect to the notification's url, or to the list when it has none.
        """
        notification = get_object_or_404(request.user.notifications, pk=pk)
        notification.mark_as_read()
        return redirect(notification.url or "mvp_community_notifications:list")


class BellView(View):
    """The bell alone, which the bell fetches to keep its count current."""

    def get(self, request):
        """Render the bell with a fresh count.

        A signed-out request gets no content rather than a redirect: htmx
        follows a redirect and would swap the sign-in page into the header.

        Args:
            request: The GET request.

        Returns:
            The bell, or an empty 204 response for a signed-out visitor.
        """
        if not request.user.is_authenticated:
            return HttpResponse(status=204)
        return render(request, "mvp_community/notifications/bell_partial.html")


class PreferencesView(LoginRequiredMixin, MVPTemplateView):
    """Which notification types reach the person on which channel."""

    template_name = "mvp_community/notifications/preferences.html"
    page_title = _("Notification preferences")
    page_lead = _("Choose which notifications you receive, and where.")
    breadcrumbs = [{"text": _("Account Center")}, {"text": _("Notifications")}]

    def get_context_data(self, **kwargs):
        """Add the types, the channels and the person's current choices."""
        context = super().get_context_data(**kwargs)
        context["preferences"] = get_notification_preferences(self.request.user)
        context["channels"] = registry.get_all_channels()
        return context
