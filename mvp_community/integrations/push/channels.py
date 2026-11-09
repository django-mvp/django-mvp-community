"""The channel that delivers a notification as a web push."""

import json
import logging

import requests
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.module_loading import import_string
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import BaseChannel
from generic_notifications.models import Notification
from generic_notifications.registry import registry
from mvp.config import MVP_CONFIG
from push_notifications.exceptions import WebPushError
from push_notifications.models import WebPushDevice

logger = logging.getLogger(__name__)

BODY_LENGTH = 400
ICON_SIZE = 192


class PushChannel(BaseChannel):
    """Deliver each notification to the browsers its recipient turned push on in.

    Push is sent as the notification is created. It has no digest, so a person
    who gets a type as a daily digest by email still gets its push at once.
    """

    key = "push"
    name = _("Push")
    supports_realtime = True
    supports_digest = False

    def recipient_language(self, user):
        """Give the language the person's push is written in.

        Django has no language per person, so this is the site's. A project
        that stores one overrides this.

        Args:
            user: The person the push is sent to.

        Returns:
            A language code.
        """
        return settings.LANGUAGE_CODE

    def icon(self, notification_type=None):
        """Give the address of the icon a push shows, or None for no icon.

        The notification type's ``push_icon`` comes first, then the
        ``MVP_COMMUNITY_PUSH_ICON`` setting, then the site's own icon from
        django-mvp's brand. Each is a static path or a URL, and is sent as an
        absolute address, built the way django-generic-notifications builds
        a notification's.

        Args:
            notification_type: The type of the notification being pushed, or
                None for the push that confirms push is on.

        Returns:
            An absolute URL, or None when there is no icon.
        """
        icon = getattr(notification_type, "push_icon", None) or getattr(
            settings, "MVP_COMMUNITY_PUSH_ICON", None
        )
        if icon and not icon.startswith(("http://", "https://", "/")):
            icon = static(icon)
        if not icon:
            try:
                resolver = import_string(MVP_CONFIG["brand"]["icon_resolver"])
                icon = resolver(None, ICON_SIZE, "light")
            except Exception:  # A project's resolver may fail in any way.
                icon = None
        if not icon:
            return None
        return Notification(url=icon).get_absolute_url()

    def payload(self, notification):
        """Build what the service worker shows for one notification.

        Args:
            notification: The notification being pushed.

        Returns:
            A JSON string with the ``title``, the ``body``, the ``url`` the
            notification opens and, when there is one, the ``icon``.
        """
        with translation.override(self.recipient_language(notification.recipient)):
            message = {
                "title": str(notification.get_subject()),
                "body": Truncator(str(notification.get_text())).chars(BODY_LENGTH),
                "url": reverse(
                    "mvp_community_notifications:open", args=[notification.pk]
                ),
            }
        try:
            notification_type = registry.get_type(notification.notification_type)
        except KeyError:
            notification_type = None
        icon = self.icon(notification_type)
        if icon:
            message["icon"] = icon
        return json.dumps(message)

    def deliver(self, subscription, payload):
        """Send one payload to one subscription, never raising.

        A subscription the push service refuses, or cannot be reached, is
        logged and skipped, so one browser never stops the others.

        Args:
            subscription: The ``WebPushDevice`` to send to.
            payload: The JSON string to send.
        """
        try:
            subscription.send_message(payload)
        except (WebPushError, requests.RequestException):
            logger.warning(
                "Push to subscription %s failed.", subscription.pk, exc_info=True
            )

    def send_test(self, subscription):
        """Send the push that tells a person it is on for their browser.

        Args:
            subscription: The ``WebPushDevice`` that was just turned on.
        """
        with translation.override(self.recipient_language(subscription.user)):
            message = {
                "title": str(_("Push notifications")),
                "body": str(_("Push is on for this browser.")),
                "url": reverse("mvp_community_notifications:preferences"),
            }
        icon = self.icon()
        if icon:
            message["icon"] = icon
        self.deliver(subscription, json.dumps(message))

    def send_now(self, notification):
        """Send one notification to each active subscription of its recipient.

        A subscription the push service refuses, or cannot be reached, is
        logged and skipped, so one browser never stops the others.

        Args:
            notification: The notification to send.
        """
        payload = self.payload(notification)
        subscriptions = WebPushDevice.objects.filter(
            user=notification.recipient, active=True
        )
        for subscription in subscriptions:
            self.deliver(subscription, payload)
