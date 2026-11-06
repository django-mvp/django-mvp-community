"""Send the demo's notification and digest emails, and print unsubscribe links in every state."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse
from generic_notifications import send_notification
from generic_notifications.digest import send_notification_digests
from generic_notifications.models import (
    NotificationFrequencyPreference,
    NotificationTypeChannelPreference,
)
from generic_notifications.registry import registry

from mvp_community.integrations.notifications.unsubscribe import UNSUBSCRIBE_SALT

REALTIME = [
    (
        "reply_received",
        "Anna replied to your question",
        "“I had the same trouble with the dative. Try the second exercise first.”",
    ),
]
DAILY = [
    ("new_follower", "Marek Nowak started following you", ""),
    ("new_follower", "Lena Fischer started following you", ""),
    ("new_follower", "Jonas Weber started following you", ""),
]
WEEKLY = [
    (
        "course_updated",
        "A1 Tenses has three new lessons",
        "The past tense with haben and sein, and a review of irregular verbs.",
    ),
    ("course_updated", "B1 Grammar was updated", ""),
]
ALWAYS = [
    (
        "security_notice",
        "New sign-in from Firefox on Linux",
        "If this wasn't you, change your password now.",
    ),
]


class Command(BaseCommand):
    """Email the regular user a notification, a security notice, a daily digest and a weekly digest."""

    help = __doc__

    def handle(self, *args, **options):
        """Set the regular user's choices, send the emails and print the links."""
        if not settings.DEBUG:
            raise CommandError("seed_notification_email only runs with DEBUG on.")
        user = get_user_model().objects.get(email="regular.user@example.com")
        NotificationTypeChannelPreference.objects.filter(user=user).delete()
        NotificationFrequencyPreference.objects.filter(user=user).delete()
        for key, frequency in [
            ("reply_received", "realtime"),
            ("new_follower", "daily"),
            ("course_updated", "weekly"),
            ("security_notice", "weekly"),
        ]:
            NotificationTypeChannelPreference.objects.create(
                user=user, notification_type=key, channel="email", enabled=True
            )
            NotificationFrequencyPreference.objects.create(
                user=user, notification_type=key, frequency=frequency
            )

        def send(rows):
            for kind, subject, text in rows:
                send_notification(
                    recipient=user,
                    notification_type=registry.get_type(kind),
                    subject=subject,
                    text=text,
                    url="/notifications/",
                )

        # Real-time types are emailed as they are sent. The others are held for
        # their digest, which the commands below send.
        send(REALTIME)
        send(DAILY)
        send(WEEKLY)
        send(ALWAYS)
        send_notification_digests(registry.get_frequency("daily"))
        send_notification_digests(registry.get_frequency("weekly"))

        def link(keys):
            token = signing.dumps(
                {"u": user.pk, "t": sorted(keys)}, salt=UNSUBSCRIBE_SALT
            )
            return reverse("mvp_community_notifications:unsubscribe", args=[token])

        self.stdout.write(
            "Sent: a notification, a security notice, a daily digest and a weekly digest."
        )
        self.stdout.write(f"  one type:      {link(['reply_received'])}")
        self.stdout.write(
            f"  a digest:      {link(['course_updated', 'security_notice'])}"
        )
        self.stdout.write(f"  invalid:       {link(['reply_received'])[:-6]}broken/")
