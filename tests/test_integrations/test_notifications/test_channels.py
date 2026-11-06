"""The notification email channel, asserted through django-post-office's queue."""

import pytest
from generic_notifications import send_notification
from generic_notifications.models import (
    Notification,
    NotificationChannel,
    NotificationFrequencyPreference,
    NotificationTypeChannelPreference,
)
from generic_notifications.registry import registry
from post_office.models import STATUS, Email

from demo.notifications import ReplyReceived, SecurityNotice
from mvp_community.integrations.notifications.channels import NotificationEmailChannel

# The root element every branded email layout draws.
LAYOUT_ROOT = "<html lang="


@pytest.fixture(autouse=True)
def queued(settings):
    """Leave email in django-post-office's queue, where it can be read."""
    # pytest-django swaps the mail backend for an in-memory one, which skips the queue.
    settings.EMAIL_BACKEND = "post_office.EmailBackend"
    settings.POST_OFFICE = {**settings.POST_OFFICE, "DEFAULT_PRIORITY": "medium"}


@pytest.fixture
def realtime_notification(person):
    """A stored notification with an email row, not yet sent."""
    notification = Notification.objects.create(
        recipient=person,
        notification_type=ReplyReceived.key,
        subject="Anna replied",
        text="Try the second exercise first.",
        url="/notifications/",
    )
    NotificationChannel.objects.create(notification=notification, channel="email")
    return notification


@pytest.fixture
def realtime(person):
    """The person chose to get replies as they happen."""
    NotificationFrequencyPreference.objects.create(
        user=person, notification_type=ReplyReceived.key, frequency="realtime"
    )


class TestNotificationEmailChannel:
    def test_a_notification_is_queued_to_the_person_as_html_on_the_layout(
        self, person, realtime
    ) -> None:
        send_notification(recipient=person, notification_type=ReplyReceived)

        email = Email.objects.get()
        assert email.to == [person.email]
        assert email.status == STATUS.queued
        assert LAYOUT_ROOT in email.html_message
        assert email.message

    def test_it_is_marked_sent_on_the_email_channel(self, person, realtime) -> None:
        notification = send_notification(
            recipient=person, notification_type=ReplyReceived
        )

        assert notification.channels.get(channel="email").sent_at is not None

    def test_with_email_off_nothing_is_queued(self, person, realtime) -> None:
        NotificationTypeChannelPreference.objects.create(
            user=person,
            notification_type=ReplyReceived.key,
            channel="email",
            enabled=False,
        )

        send_notification(recipient=person, notification_type=ReplyReceived)

        assert Email.objects.count() == 0

    def test_a_person_with_no_address_is_sent_nothing(self, person, realtime) -> None:
        person.email = ""
        person.save()

        send_notification(recipient=person, notification_type=ReplyReceived)

        assert Email.objects.count() == 0

    def test_a_digest_frequency_holds_the_email_back_for_the_digest(
        self, person
    ) -> None:
        NotificationFrequencyPreference.objects.create(
            user=person, notification_type=ReplyReceived.key, frequency="daily"
        )

        send_notification(recipient=person, notification_type=ReplyReceived)

        assert Email.objects.count() == 0

    def test_an_always_sent_type_is_sent_at_once_whatever_frequency_is_stored(
        self, person
    ) -> None:
        NotificationFrequencyPreference.objects.create(
            user=person, notification_type=SecurityNotice.key, frequency="weekly"
        )

        send_notification(recipient=person, notification_type=SecurityNotice)

        assert [email.to for email in Email.objects.all()] == [[person.email]]


class TestRecipientLanguage:
    class German(NotificationEmailChannel):
        def recipient_language(self, user):
            return "de"

    def test_the_site_language_is_the_default(self, person, settings) -> None:
        settings.LANGUAGE_CODE = "fr"

        assert NotificationEmailChannel().recipient_language(person) == "fr"

    def test_a_subclass_chooses_the_language_a_notification_is_written_in(
        self, realtime_notification
    ) -> None:
        self.German().send_now(realtime_notification)

        assert 'lang="de"' in Email.objects.get().html_message

    def test_the_site_language_is_used_when_the_subclass_does_not_choose(
        self, realtime_notification
    ) -> None:
        NotificationEmailChannel().send_now(realtime_notification)

        assert 'lang="en-us"' in Email.objects.get().html_message

    def test_a_digest_is_written_in_the_language_the_subclass_chooses(
        self, realtime_notification
    ) -> None:
        self.German().send_digest(
            Notification.objects.filter(pk=realtime_notification.pk),
            registry.get_frequency("daily"),
        )

        assert 'lang="de"' in Email.objects.get().html_message


class TestEmailTemplates:
    def test_a_project_template_under_the_realtime_name_replaces_the_packages(
        self, realtime_notification, settings, tmp_path
    ) -> None:
        folder = tmp_path / "notifications" / "email" / "realtime"
        folder.mkdir(parents=True)
        (folder / "message.html").write_text("<p>project-template</p>")
        templates = [dict(engine) for engine in settings.TEMPLATES]
        templates[0]["DIRS"] = [tmp_path, *templates[0]["DIRS"]]
        settings.TEMPLATES = templates

        NotificationEmailChannel().send_now(realtime_notification)

        email = Email.objects.get()
        assert "project-template" in email.html_message
        assert LAYOUT_ROOT not in email.html_message
