"""The notifications page, the bell's refresh and the preferences page."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from generic_notifications.models import Notification
from generic_notifications.utils import get_notifications
from mvp.views import MVPListView


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
