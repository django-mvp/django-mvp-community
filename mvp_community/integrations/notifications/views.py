"""The notifications page, the bell's refresh and the preferences page."""

from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from generic_notifications.models import Notification
from generic_notifications.preferences import (
    get_notification_preferences,
    save_notification_preferences,
)
from generic_notifications.registry import registry
from generic_notifications.utils import get_notifications
from mvp.views import MVPListView, MVPTemplateView

from .unsubscribe import UnsubscribeLink

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

        A push or an email links here for as long as it is kept, which can be
        long after the project deleted the notification. Such a link, and one
        to another person's notification, goes to the list and changes nothing.
        The two get the same answer, so the address never tells anyone whether
        another person's notification exists.

        Args:
            request: The GET request.
            pk: The notification's primary key.

        Returns:
            A redirect to the notification's url, or to the list when it has
            none, it points at another site, or the person has no notification
            with this key.
        """
        notification = request.user.notifications.filter(pk=pk).first()
        if notification is None:
            return redirect("mvp_community_notifications:list")
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
        preferences = get_notification_preferences(self.request.user)
        for row in preferences:
            # A type the project always sends on a channel is too important to
            # wait for a digest: its email always arrives as it happens.
            row["offers_frequency"] = not row["notification_type"].required_channels
        context["preferences"] = preferences
        context["channels"] = registry.get_all_channels()
        # How often an email comes means nothing without the email channel.
        email_registered = any(c.key == "email" for c in context["channels"])
        context["frequencies"] = [
            (frequency.key, FREQUENCY_LABELS.get(frequency.key, frequency.name))
            for frequency in registry.get_all_frequencies()
            if email_registered
        ]
        if any(c.key == "push" for c in context["channels"]):
            # Imported here so the notifications extra never needs the push one.
            from mvp_community.integrations.push.subscriptions import card_context

            context["push"] = card_context(self.request)
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


@method_decorator([csrf_exempt, login_not_required], name="dispatch")
class UnsubscribeView(MVPTemplateView):
    """Turn off the email an unsubscribe link was sent with, signed in or not.

    A POST is what a mail app sends from the email's unsubscribe header.
    """

    template_name = "mvp_community/notifications/unsubscribe.html"
    page_title = _("Unsubscribe")

    def outcome_page(self, outcome, link):
        """Render the page for one of its states.

        Args:
            outcome: ``confirm``, ``done``, ``already`` or ``invalid``.
            link: The unsubscribe link, or None when it was not valid.

        Returns:
            The rendered page.
        """
        types = link.types if link else []
        return self.render_to_response(
            self.get_context_data(outcome=outcome, types=types)
        )

    def get(self, request, token):
        """Ask the person to confirm, so a mail scanner opening the link changes nothing.

        Args:
            request: The GET request.
            token: The signed token from the address.

        Returns:
            The confirm, already or invalid page.
        """
        link = UnsubscribeLink.read(token)
        if link is None:
            return self.outcome_page("invalid", None)
        return self.outcome_page("confirm" if link.emailed() else "already", link)

    def post(self, request, token):
        """Turn the email off, from the page's button or a mail app's one-click header.

        A mail app posts ``List-Unsubscribe=One-Click`` and is answered with no page.

        Args:
            request: The POST request.
            token: The signed token from the address.

        Returns:
            Status 200 or 400 with no body for a one-click request, otherwise
            the done, already or invalid page.
        """
        link = UnsubscribeLink.read(token)
        one_click = request.POST.get("List-Unsubscribe") == "One-Click"
        if link is None:
            if one_click:
                return HttpResponse(status=400)
            return self.outcome_page("invalid", None)
        changed = link.turn_off()
        if one_click:
            return HttpResponse(status=200)
        return self.outcome_page("done" if changed else "already", link)
