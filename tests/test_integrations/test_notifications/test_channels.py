"""The notification email channel, asserted through django-post-office's queue."""

import pytest
from django.core import signing
from generic_notifications import send_notification
from generic_notifications.digest import send_notification_digests
from generic_notifications.models import (
    Notification,
    NotificationChannel,
    NotificationFrequencyPreference,
    NotificationTypeChannelPreference,
)
from generic_notifications.registry import registry
from post_office.models import STATUS, Email

from demo.notifications import (
    CourseUpdated,
    NewFollower,
    ReplyReceived,
    SecurityNotice,
)
from mvp_community.integrations.notifications.channels import NotificationEmailChannel
from mvp_community.integrations.notifications.unsubscribe import UnsubscribeLink

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


class TestDigests:
    # ReplyReceived declares no frequency, so it defaults to the library's daily.

    @pytest.fixture
    def weekly(self, person):
        """The person chose to get course updates once a week."""
        NotificationFrequencyPreference.objects.create(
            user=person, notification_type=CourseUpdated.key, frequency="weekly"
        )

    def test_a_person_with_unread_notifications_gets_one_daily_digest(
        self, person
    ) -> None:
        for _ in range(2):
            send_notification(recipient=person, notification_type=ReplyReceived)

        send_notification_digests(registry.get_frequency("daily"))

        email = Email.objects.get()
        assert email.to == [person.email]
        assert LAYOUT_ROOT in email.html_message
        assert ReplyReceived.name in email.html_message

    def test_a_person_with_nothing_unread_gets_no_digest(self, person) -> None:
        send_notification_digests(registry.get_frequency("daily"))

        assert Email.objects.count() == 0

    def test_a_read_notification_is_left_out(self, person) -> None:
        send_notification(
            recipient=person, notification_type=ReplyReceived
        ).mark_as_read()

        send_notification_digests(registry.get_frequency("daily"))

        assert Email.objects.count() == 0

    def test_a_digest_is_sent_once(self, person) -> None:
        send_notification(recipient=person, notification_type=ReplyReceived)

        send_notification_digests(registry.get_frequency("daily"))
        send_notification_digests(registry.get_frequency("daily"))

        assert Email.objects.count() == 1

    def test_a_weekly_choice_is_in_the_weekly_digest_and_not_the_daily(
        self, person, weekly
    ) -> None:
        send_notification(recipient=person, notification_type=CourseUpdated)

        send_notification_digests(registry.get_frequency("daily"))
        assert Email.objects.count() == 0

        send_notification_digests(registry.get_frequency("weekly"))
        assert [email.to for email in Email.objects.all()] == [[person.email]]

    def test_each_digest_holds_only_the_types_chosen_for_its_frequency(
        self, person, weekly
    ) -> None:
        send_notification(recipient=person, notification_type=CourseUpdated)
        send_notification(recipient=person, notification_type=ReplyReceived)

        send_notification_digests(registry.get_frequency("daily"))

        html = Email.objects.get().html_message
        assert ReplyReceived.name in html
        assert CourseUpdated.name not in html


class TestUnsubscribeHeaders:
    @pytest.fixture(autouse=True)
    def signing_clock(self, monkeypatch):
        """Sign every token in the same second.

        A token carries the second it was signed in, so an address built here
        and one built during the send differ as text whenever the clock ticks
        between them.
        """
        monkeypatch.setattr(signing.TimestampSigner, "timestamp", lambda self: "1")

    @pytest.fixture
    def link(self, person):
        return UnsubscribeLink.for_email(person, [ReplyReceived.key])

    def test_a_notification_carries_the_address_and_the_one_click_header(
        self, person, realtime, link
    ) -> None:
        send_notification(recipient=person, notification_type=ReplyReceived)

        email = Email.objects.get()
        assert email.headers["List-Unsubscribe"] == f"<{link.url()}>"
        assert email.headers["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"

    def test_the_footer_links_to_the_same_address(self, person, realtime, link) -> None:
        send_notification(recipient=person, notification_type=ReplyReceived)

        email = Email.objects.get()
        assert f'href="{link.url()}"' in email.html_message
        assert link.url() in email.message

    def test_a_digest_carries_an_address_naming_every_type_in_it(self, person) -> None:
        send_notification(recipient=person, notification_type=ReplyReceived)
        send_notification(recipient=person, notification_type=NewFollower)

        send_notification_digests(registry.get_frequency("daily"))

        email = Email.objects.get()
        address = email.headers["List-Unsubscribe"].strip("<>")
        expected = UnsubscribeLink.for_email(
            person, [ReplyReceived.key, NewFollower.key]
        ).url()
        assert address == expected
        assert email.headers["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"

    def test_an_always_sent_type_carries_no_header_and_no_link(self, person) -> None:
        send_notification(recipient=person, notification_type=SecurityNotice)

        email = Email.objects.get()
        assert "List-Unsubscribe" not in email.headers
        assert "List-Unsubscribe-Post" not in email.headers
        assert "/notifications/unsubscribe/" not in email.html_message
        assert "/notifications/unsubscribe/" not in email.message
