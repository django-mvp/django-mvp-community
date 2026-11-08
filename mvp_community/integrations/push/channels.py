"""The channel that delivers a notification as a web push."""

from django.utils.translation import gettext_lazy as _
from generic_notifications.channels import BaseChannel


class PushChannel(BaseChannel):
    """Deliver each notification to the browsers its recipient turned push on in.

    Push is sent as the notification is created. It has no digest, so a person
    who gets a type as a daily digest by email still gets its push at once.
    """

    key = "push"
    name = _("Push")
    supports_realtime = True
    supports_digest = False

    def send_now(self, notification):
        """Send one notification to the recipient's browsers.

        Args:
            notification: The notification to send.
        """
