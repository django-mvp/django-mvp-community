"""The notifications page, the bell's refresh and the preferences page."""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from generic_notifications.models import Notification, NotificationTypeChannelPreference
from generic_notifications.preferences import (
    get_notification_preferences,
    save_notification_preferences,
)
from generic_notifications.registry import registry
from generic_notifications.utils import get_notifications
from mvp.views import MVPListView, MVPTemplateView

from mvp_community.templatetags.mvp_community_notifications import UNSUBSCRIBE_SALT

FREQUENCY_LABELS = {
    "realtime": _("As it happens"),
    "daily": _("Daily digest"),
    "weekly": _("Weekly digest"),
}


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
            A redirect to the notification's url, or to the list when it has
            none or it points at another site.
        """
        notification = get_object_or_404(request.user.notifications, pk=pk)
        notification.mark_as_read()
        # A url can be built from what someone typed, so a link off this site
        # is never followed from here.
        if notification.url and url_has_allowed_host_and_scheme(
            notification.url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(notification.url)
        return redirect("mvp_community_notifications:list")


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
        context["frequencies"] = [
            (frequency.key, FREQUENCY_LABELS.get(frequency.key, frequency.name))
            for frequency in registry.get_all_frequencies()
        ]
        return context

    def post(self, request):
        """Save the choices, say so, and come back to the page.

        Args:
            request: The POST request carrying one ``<type>__<channel>`` field
                for each choice switched on.

        Returns:
            A redirect to the preferences page.
        """
        save_notification_preferences(request.user, request.POST)
        messages.success(request, _("Your notification preferences are saved."))
        return redirect("mvp_community_notifications:preferences")


@method_decorator(csrf_exempt, name="dispatch")
class UnsubscribeView(MVPTemplateView):
    """Turn off the email an unsubscribe link was sent with, signed in or not.

    A POST is what a mail app sends from the email's unsubscribe header.
    """

    template_name = "mvp_community/notifications/unsubscribe.html"
    page_title = _("Unsubscribe")

    def unsubscribe(self, token):
        """Read the token and turn email off for its types.

        Args:
            token: The signed token from the link.

        Returns:
            The outcome (``done``, ``already`` or ``invalid``) and the types.
        """
        try:
            data = signing.loads(token, salt=UNSUBSCRIBE_SALT)
            user = get_user_model().objects.get(pk=data["u"])
        except (signing.BadSignature, KeyError, TypeError, get_user_model().DoesNotExist):
            return "invalid", []
        types = [t for t in registry.get_all_types() if t.key in data.get("t", [])]
        if not types:
            return "invalid", []
        changed = False
        for notification_type in types:
            enabled = "email" in [c.key for c in notification_type.get_enabled_channels(user)]
            if enabled:
                NotificationTypeChannelPreference.objects.update_or_create(
                    user=user,
                    notification_type=notification_type.key,
                    channel="email",
                    defaults={"enabled": False},
                )
                changed = True
        return ("done" if changed else "already"), types

    def get(self, request, token):
        """Unsubscribe and say what was turned off."""
        outcome, types = self.unsubscribe(token)
        return self.render_to_response(
            self.get_context_data(outcome=outcome, types=types)
        )

    def post(self, request, token):
        """Unsubscribe without a page, as a mail app's one-click button asks."""
        outcome, _types = self.unsubscribe(token)
        return HttpResponse(status=400 if outcome == "invalid" else 200)
