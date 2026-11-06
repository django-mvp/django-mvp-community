"""Management command that creates the demo project's sign-in accounts."""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

PASSWORD = "password"
DEFAULT_SITE_DOMAIN = "localhost:8000"

ACCOUNTS = [
    ("regular.user@example.com", {"is_staff": False, "is_superuser": False}),
    ("staff.user@example.com", {"is_staff": True, "is_superuser": False}),
    ("super.user@example.com", {"is_staff": True, "is_superuser": True}),
]


class Command(BaseCommand):
    """Create the sign-in accounts and give the site the address emails link to."""

    help = "Create the demo sign-in accounts."

    def handle(self, *args, **options):
        """Refuse unless DEBUG is on, then set the site's domain and create or reset each account."""
        # Known passwords: refusing to run without DEBUG is what keeps them off a
        # deployed site.
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo creates accounts with a known password and only "
                "runs with DEBUG on."
            )

        # The address every link in an email is built from. It is the one the
        # person reading the email reaches the demo at.
        Site.objects.filter(pk=settings.SITE_ID).update(
            domain=os.environ.get("DEMO_SITE_DOMAIN", DEFAULT_SITE_DOMAIN)
        )

        user_model = get_user_model()
        # The address is the identifier whichever field the project made its
        # username, so a project that swapped in a custom user model still gets
        # three accounts rather than an integrity error.
        username_field = user_model.USERNAME_FIELD

        for email, flags in ACCOUNTS:
            user, created = user_model.objects.get_or_create(
                **{username_field: email}, defaults={"email": email, **flags}
            )
            for attribute, value in flags.items():
                setattr(user, attribute, value)
            user.set_password(PASSWORD)
            user.save()
            self.stdout.write(f"  {'created' if created else 'updated'}  {email}")

        self.stdout.write(
            self.style.SUCCESS(f"\nAll three sign in with the password {PASSWORD!r}.")
        )
