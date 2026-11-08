"""Management command that gives the demo's regular user push subscriptions."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from push_notifications.models import WebPushDevice

EMAIL = "regular.user@example.com"

# (endpoint, user agent, days since push was turned on)
SUBSCRIPTIONS = [
    (
        "https://web.push.apple.com/demo-iphone",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 "
        "Safari/604.1",
        12,
    ),
    (
        "https://fcm.googleapis.com/fcm/send/demo-windows",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        40,
    ),
]


class Command(BaseCommand):
    """Give the regular user two push subscriptions to walk the list with."""

    help = "Give the demo's regular user two push subscriptions."

    def handle(self, *args, **options):
        """Refuse unless DEBUG is on, then rebuild the regular user's subscriptions.

        The demo is served over plain HTTP, where a browser cannot subscribe
        itself, so these are the only way to see the list. Nothing is sent to
        them: their endpoints are on the allowed push services but are not real.
        """
        if not settings.DEBUG:
            raise CommandError("seed_push only runs with DEBUG on.")
        user = get_user_model().objects.get(email=EMAIL)
        WebPushDevice.objects.filter(user=user).delete()
        now = timezone.now()
        for endpoint, user_agent, days in SUBSCRIPTIONS:
            subscription = WebPushDevice.objects.create(
                user=user,
                registration_id=endpoint,
                p256dh="demo-p256dh-key",
                auth="demo-auth",
                name=user_agent,
            )
            WebPushDevice.objects.filter(pk=subscription.pk).update(
                date_created=now - timedelta(days=days)
            )
        self.stdout.write(f"  {len(SUBSCRIPTIONS):>3}  {EMAIL}")
