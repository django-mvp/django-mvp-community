"""The notifications page, the bell's refresh and the preferences page."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from generic_notifications.preferences import (
    get_notification_preferences,
    save_notification_preferences,
)
from generic_notifications.registry import registry
from generic_notifications.utils import get_notifications, get_unread_count, mark_notifications_as_read
from mvp.views import MVPTemplateView

PER_PAGE = 20


class NotificationListView(LoginRequiredMixin, MVPTemplateView):
    """A person's notifications on the site, newest first."""

    template_name = "mvp_community/notifications/list.html"
    page_title = _("Notifications")
    breadcrumbs = [{"text": _("Notifications")}]

    def get_context_data(self, **kwargs):
        """Add one page of the person's notifications."""
        context = super().get_context_data(**kwargs)
        paginator = Paginator(get_notifications(self.request.user), PER_PAGE)
        context["page_obj"] = paginator.get_page(self.request.GET.get("page"))
        return context


class MarkAllReadView(LoginRequiredMixin, View):
    """Mark every one of the person's notifications read."""

    def post(self, request):
        """Mark them read and go back to the list."""
        mark_notifications_as_read(request.user)
        return redirect("mvp_community_notifications:list")


class OpenNotificationView(LoginRequiredMixin, View):
    """Mark a notification read and follow its link."""

    def get(self, request, pk):
        """Mark it read, then redirect to where it points."""
        notification = get_object_or_404(request.user.notifications, pk=pk)
        notification.mark_as_read()
        return redirect(notification.url or "mvp_community_notifications:list")


class BellView(LoginRequiredMixin, View):
    """The bell alone, which the bell fetches to keep its count current."""

    def get(self, request):
        """Render the bell with a fresh count."""
        return render(
            request,
            "mvp_community/notifications/bell_partial.html",
            {"notifications_unread": get_unread_count(request.user)},
        )


class PreferencesView(LoginRequiredMixin, MVPTemplateView):
    """Which notification types reach the person on which channel."""

    template_name = "mvp_community/notifications/preferences.html"
    page_title = _("Notification preferences")
    page_subtitle = _("Choose which notifications you receive, and where")
    breadcrumbs = [{"text": _("Account Center")}, {"text": _("Notifications")}]

    def get_context_data(self, **kwargs):
        """Add the types, the channels and the person's current choices."""
        context = super().get_context_data(**kwargs)
        context["preferences"] = get_notification_preferences(self.request.user)
        context["channels"] = registry.get_all_channels()
        return context

    def post(self, request):
        """Save the choices and come back to the page."""
        save_notification_preferences(request.user, request.POST)
        messages.success(request, _("Your notification preferences are saved."))
        return redirect("mvp_community_notifications:preferences")
