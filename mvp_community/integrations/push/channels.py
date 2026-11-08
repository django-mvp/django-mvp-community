"""The channel that delivers a notification as a web push."""

import json
import logging

import requests
from django.conf import settings
from django.urls import reverse
from django.utils import translation
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import BaseChannel
from push_notifications.exceptions import WebPushError
from push_notifications.models import WebPushDevice

logger = logging.getLogger(__name__)

BODY_LENGTH = 400


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

    def payload(self, notification):
        """Build what the service worker shows for one notification.

        Args:
            notification: The notification being pushed.

        Returns:
            A JSON string with the ``title``, the ``body`` and the ``url`` the
            notification opens.
        """
        with translation.override(self.recipient_language(notification.recipient)):
            return json.dumps(
                {
                    "title": str(notification.get_subject()),
                    "body": Truncator(str(notification.get_text())).chars(BODY_LENGTH),
                    "url": reverse(
                        "mvp_community_notifications:open", args=[notification.pk]
                    ),
                }
            )

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
            try:
                subscription.send_message(payload)
            except (WebPushError, requests.RequestException):
                logger.warning(
                    "Push to subscription %s failed.", subscription.pk, exc_info=True
                )
