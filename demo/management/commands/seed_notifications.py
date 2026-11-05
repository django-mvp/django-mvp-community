"""Management command that gives the demo accounts notifications in every state."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from generic_notifications.models import Notification, NotificationChannel

# (type, subject, text, url, read)
SAMPLES = [
    (
        "reply_received",
        "Anna replied to your question",
        "“I had the same trouble with the dative. Try the second exercise first.”",
        "/",
        False,
    ),
    ("new_follower", "Marek Nowak started following you", "", "/", False),
    (
        "course_updated",
        "A1 Tenses has three new lessons",
        "The past tense with haben and sein, and a review of irregular verbs.",
        "/",
        False,
    ),
    (
        "security_notice",
        "New sign-in from Firefox on Linux",
        "If this wasn't you, change your password now.",
        "",
        False,
    ),
    (
        "reply_received",
        "Jonas Weber replied to “Which article goes with Mädchen?”",
        "“It is das, because of the -chen ending. Every word ending in -chen is "
        "neuter, whatever it means, so das Mädchen, das Brötchen, das Häuschen. "
        "This one surprises nearly everyone, so don't worry.”",
        "/",
        True,
    ),
    ("course_updated", "B1 Grammar was updated", "", "/", True),
    ("new_follower", "Lena Fischer started following you", "", "/", True),
    ("security_notice", "Your password was changed", "", "", True),
]


class Command(BaseCommand):
    """Replace the demo accounts' notifications with a fixed set."""

    help = (
        "Give the demo accounts notifications: many for the regular user, "
        "a few for the superuser, none for staff."
    )

    def handle(self, *args, **options):
        """Refuse unless DEBUG is on, then rebuild each account's notifications."""
        if not settings.DEBUG:
            raise CommandError("seed_notifications only runs with DEBUG on.")
        users = get_user_model().objects
        now = timezone.now()
        plan = {
            "regular.user@example.com": 46,  # more than two pages
            "super.user@example.com": 3,
            "staff.user@example.com": 0,  # the empty page
        }
        for email, count in plan.items():
            user = users.get(email=email)
            Notification.objects.filter(recipient=user).delete()
            for index in range(count):
                kind, subject, text, url, read = SAMPLES[index % len(SAMPLES)]
                read = read or index >= len(SAMPLES)
                notification = Notification.objects.create(
                    recipient=user,
                    notification_type=kind,
                    subject=subject,
                    text=text,
                    url=url,
                    read=now if read else None,
                )
                added = now - timedelta(minutes=7 + index * 95)
                Notification.objects.filter(pk=notification.pk).update(added=added)
                NotificationChannel.objects.create(
                    notification=notification, channel="website", sent_at=added
                )
            self.stdout.write(f"  {count:>3}  {email}")
