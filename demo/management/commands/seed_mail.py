"""Management command that gives the demo a stored email template and a delivery log."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from post_office import mail
from post_office.models import Email, EmailTemplate

LAYOUT = '{% extends "mvp/email/base.html" %}'

ENGLISH_BODY = (
    "{% block body %}<h1>Welcome</h1>"
    "<p>Your account is ready. Everything you do here is kept in the "
    "delivery log.</p>{% endblock %}"
)

# The layout's default footer is English: django-mvp ships no German catalogue.
GERMAN_BODY = (
    "{% block body %}<h1>Willkommen</h1>"
    "<p>Ihr Konto ist bereit. Alles, was Sie hier tun, steht im "
    "Zustellprotokoll.</p>{% endblock %}"
    "{% block footer %}<p>Gesendet von {{ site_name }}.</p>{% endblock %}"
)


class Command(BaseCommand):
    """Replace the demo's stored template and delivery log with a fixed set."""

    help = (
        "Create the stored template 'welcome' with a German translation, "
        "and send it once in each language."
    )

    def handle(self, *args, **options):
        """Refuse unless DEBUG is on, then rebuild the template and send it twice."""
        if not settings.DEBUG:
            raise CommandError("seed_mail only runs with DEBUG on.")

        Email.objects.filter(template__name="welcome").delete()
        EmailTemplate.objects.filter(name="welcome").delete()
        english = EmailTemplate.objects.create(
            name="welcome",
            description="Sent to a person when their account is created.",
            subject="Welcome",
            html_content=LAYOUT + ENGLISH_BODY,
        )
        EmailTemplate.objects.create(
            name="welcome",
            language="de",
            default_template=english,
            subject="Willkommen",
            html_content=LAYOUT + GERMAN_BODY,
        )

        for language in ("en", "de"):
            with translation.override(language):
                mail.send(
                    "regular.user@example.com",
                    settings.DEFAULT_FROM_EMAIL,
                    template="welcome",
                    language="" if language == "en" else language,
                )
            self.stdout.write(f"  sent  welcome ({language})")
