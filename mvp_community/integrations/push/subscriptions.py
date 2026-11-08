"""What the preferences page needs to draw the push card."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from push_notifications.models import WebPushDevice
from push_notifications.settings import PUSH_NOTIFICATIONS_SETTINGS
from py_vapid import Vapid01
from py_vapid.utils import b64urlencode
from ua_parser import parse

ALLOWED_PUSH_HOSTS = (
    "fcm.googleapis.com",
    "updates.push.services.mozilla.com",
    "web.push.apple.com",
)
ALLOWED_PUSH_SUFFIXES = (".notify.windows.com", ".push.apple.com")
SESSION_KEY = "mvp_community_push_turned_on"
HANDHELD_DEVICES = {"iPhone": "phone", "iPad": "tablet"}


def application_server_key():
    """Give the public key the browser needs to subscribe to this site's push.

    It is derived from ``WP_PRIVATE_KEY`` each time, because the card is drawn
    once per preferences page.

    Returns:
        The raw public key as URL-safe base64.
    """
    private_key = PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"]
    if Path(str(private_key)).is_file():
        vapid = Vapid01.from_file(str(private_key))
    else:
        vapid = Vapid01.from_string(private_key)
    raw = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    return b64urlencode(raw)


def is_push_endpoint(url):
    """Say whether a URL is on a push service the major browsers use.

    Only these are accepted, so a signed-in person cannot make the server post
    to an address of their choosing.

    Args:
        url: The endpoint a browser sent.

    Returns:
        True for an ``https://`` URL on one of the allowed push services.
    """
    try:
        parts = urlsplit(url)
        host = parts.hostname
        parts.port  # noqa: B018
    except ValueError:
        return False
    if parts.scheme != "https" or parts.username or parts.password or not host:
        return False
    return host in ALLOWED_PUSH_HOSTS or host.endswith(ALLOWED_PUSH_SUFFIXES)


@dataclass(frozen=True)
class Browser:
    """A browser as read from the user agent it subscribed with.

    Attributes:
        family: The browser's name, such as ``Chrome``, or an empty string when
            the user agent cannot be read.
        place: The device for an iPhone or iPad, the operating system otherwise.
        kind: ``phone``, ``tablet`` or ``computer``.
    """

    family: str
    place: str
    kind: str

    @classmethod
    def from_user_agent(cls, user_agent):
        """Read a browser from a user agent string.

        Args:
            user_agent: The ``User-Agent`` header the browser sent.

        Returns:
            The browser, with empty names when nothing could be read.
        """
        result = parse(user_agent or "")
        family = (result.user_agent.family if result.user_agent else "") or ""
        family = family.removeprefix("Mobile ").removesuffix(" Mobile")
        if family == "Other":
            family = ""
        system = (result.os.family if result.os else "") or ""
        device = (result.device.family if result.device else "") or ""
        if device in HANDHELD_DEVICES:
            return cls(family, device, HANDHELD_DEVICES[device])
        place = "" if system == "Other" else system
        kind = "phone" if place == "Android" else "computer"
        return cls(family, place, kind)

    @property
    def label(self):
        """Name the browser for a person, such as ``Chrome on Android``.

        Returns:
            A translatable string.
        """
        if not self.family:
            return _("Unknown browser")
        if not self.place:
            return self.family
        return _("%(family)s on %(place)s") % {
            "family": self.family,
            "place": self.place,
        }


def card_context(request):
    """Build what the push card renders for the signed-in person.

    Args:
        request: The preferences page's request.

    Returns:
        A dict with the person's active ``subscriptions``, newest first,
        whether push was ``just_turned_on`` (read once from the session), the
        ``application_server_key`` the browser subscribes with, and the
        ``worker_url`` and ``subscribe_url`` the card's script uses. The URLs
        resolve when they are rendered, so a project that has not included the
        push routes fails on the card, not on every page.
    """
    return {
        "subscriptions": WebPushDevice.objects.filter(
            user=request.user, active=True
        ).order_by("-date_created", "-pk"),
        "just_turned_on": bool(request.session.pop(SESSION_KEY, False)),
        "application_server_key": application_server_key(),
        "worker_url": reverse_lazy("mvp_community_push:worker"),
        "subscribe_url": reverse_lazy("mvp_community_push:subscribe"),
    }
