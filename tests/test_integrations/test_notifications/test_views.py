"""The notifications extra's views, asserted as rendered through the demo."""

import re

import pytest
from django.conf import settings
from django.contrib.messages import SUCCESS, get_messages
from django.core import signing
from django.db import connection
from django.shortcuts import resolve_url
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from generic_notifications import send_notification
from generic_notifications.channels import EmailChannel, WebsiteChannel
from generic_notifications.frequencies import DailyFrequency
from generic_notifications.models import NotificationTypeChannelPreference
from generic_notifications.preferences import get_notification_preferences
from generic_notifications.registry import registry
from generic_notifications.types import NotificationType
from generic_notifications.utils import get_unread_count

from demo.notifications import NewFollower, ReplyReceived, SecurityNotice
from mvp_community.integrations.notifications.unsubscribe import UnsubscribeLink
from mvp_community.integrations.notifications.views import PreferencesView
from mvp_community.templatetags.mvp_community_notifications import UNSUBSCRIBE_SALT

SIGN_IN_URL = resolve_url(settings.LOGIN_URL)
LIST_URL = reverse("mvp_community_notifications:list")
MARK_ALL_READ_URL = reverse("mvp_community_notifications:mark_all_read")


class TestNotificationListView:
    def test_signed_out_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(LIST_URL)

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)

    def test_it_lists_only_the_persons_own_newest_first(
        self, client, signed_in, make_notifications, django_user_model
    ) -> None:
        stranger = django_user_model.objects.create_user("stranger", password="x")
        own = make_notifications(3)
        make_notifications(2, recipient=stranger)

        response = client.get(LIST_URL)

        assert list(response.context["page_obj"]) == own

    def test_a_read_one_is_told_apart_from_an_unread_one(
        self, client, signed_in, make_notifications
    ) -> None:
        # The row hides its unread dot with opacity-0 on a read notification;
        # the row component is published markup, so that class is the hook.
        first, second, _third = make_notifications(3)
        first.mark_as_read()
        second.mark_as_read()

        content = client.get(LIST_URL).content.decode()

        assert content.count("opacity-0") == 2

    def test_twenty_to_a_page_and_the_rest_on_page_two(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(25)

        first = client.get(LIST_URL).context["page_obj"]
        second = client.get(LIST_URL, {"page": 2}).context["page_obj"]

        assert (len(first), len(second)) == (20, 5)

    def test_no_notifications_draws_the_empty_state(self, client, signed_in) -> None:
        response = client.get(LIST_URL)

        assert response.status_code == 200
        assert "mvp-list-empty" in response.content.decode()

    def test_notifications_draw_no_empty_state(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(1)

        assert "mvp-list-empty" not in client.get(LIST_URL).content.decode()

    def test_the_page_costs_the_same_queries_for_one_as_for_several(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(1)
        # The first request fills the site cache, which later ones do not pay for.
        client.get(LIST_URL)
        with CaptureQueriesContext(connection) as one:
            client.get(LIST_URL)
        make_notifications(8)

        with CaptureQueriesContext(connection) as several:
            client.get(LIST_URL)

        assert len(several) == len(one)


class TestOpenNotificationView:
    def test_signed_out_is_sent_to_sign_in(self, client, notification) -> None:
        client.logout()

        response = client.get(
            reverse("mvp_community_notifications:open", args=[notification.pk])
        )

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)

    def test_opening_marks_it_read_and_goes_to_its_url(
        self, client, signed_in, notification
    ) -> None:
        response = client.get(
            reverse("mvp_community_notifications:open", args=[notification.pk])
        )

        notification.refresh_from_db()
        assert notification.read is not None
        assert response["Location"] == notification.url

    def test_a_link_to_another_site_goes_to_the_list_instead(
        self, client, signed_in, make_notifications
    ) -> None:
        (notification,) = make_notifications(1)
        notification.url = "https://elsewhere.example/"
        notification.save()

        response = client.get(
            reverse("mvp_community_notifications:open", args=[notification.pk])
        )

        notification.refresh_from_db()
        assert notification.read is not None
        assert response["Location"] == reverse("mvp_community_notifications:list")

    def test_another_persons_is_not_found_and_stays_unread(
        self, client, signed_in, make_notifications, django_user_model
    ) -> None:
        stranger = django_user_model.objects.create_user("stranger", password="x")
        (theirs,) = make_notifications(1, recipient=stranger)

        response = client.get(
            reverse("mvp_community_notifications:open", args=[theirs.pk])
        )

        theirs.refresh_from_db()
        assert (response.status_code, theirs.read) == (404, None)

    def test_one_with_no_url_goes_to_the_list(
        self, client, signed_in, make_notifications
    ) -> None:
        (bare,) = make_notifications(1)

        response = client.get(
            reverse("mvp_community_notifications:open", args=[bare.pk])
        )

        assert response["Location"] == LIST_URL


class TestMarkAllReadView:
    def test_signed_out_is_sent_to_sign_in(self, client, db) -> None:
        response = client.post(MARK_ALL_READ_URL)

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)

    def test_it_leaves_no_site_notification_unread_and_goes_back_to_the_list(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(3)

        response = client.post(MARK_ALL_READ_URL)

        assert response.status_code == 302
        assert response["Location"] == LIST_URL
        assert signed_in.notifications.filter(read__isnull=True).count() == 0

    def test_it_leaves_another_persons_notifications_unread(
        self, client, signed_in, make_notifications, django_user_model
    ) -> None:
        stranger = django_user_model.objects.create_user("stranger", password="x")
        make_notifications(2, recipient=stranger)

        client.post(MARK_ALL_READ_URL)

        assert stranger.notifications.filter(read__isnull=True).count() == 2

    def test_an_unread_one_sent_only_by_email_stays_unread(
        self, client, signed_in
    ) -> None:
        ReplyReceived.enable_channel(signed_in, EmailChannel)
        ReplyReceived.disable_channel(signed_in, WebsiteChannel)
        by_email = send_notification(
            recipient=signed_in, notification_type=ReplyReceived, subject="Email only"
        )

        client.post(MARK_ALL_READ_URL)

        by_email.refresh_from_db()
        assert by_email.read is None

    def test_a_get_is_refused(self, client, signed_in) -> None:
        assert client.get(MARK_ALL_READ_URL).status_code == 405


class TestBellView:
    BELL_URL = reverse("mvp_community_notifications:bell")

    def test_it_returns_the_bell_with_the_current_count(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(4)

        content = client.get(self.BELL_URL).content.decode()

        assert 'id="mvp-community-bell"' in content
        assert '<span aria-hidden="true">4</span>' in content

    def test_it_returns_the_bell_alone_not_the_page(self, client, signed_in) -> None:
        assert "<html" not in client.get(self.BELL_URL).content.decode()

    def test_signed_out_gets_no_content_and_no_redirect(self, client, db) -> None:
        response = client.get(self.BELL_URL)

        assert (response.status_code, response.content) == (204, b"")


PREFERENCES_URL = reverse("mvp_community_notifications:preferences")


def toggle(page: str, name: str) -> str:
    """Return the opening tag of the control named ``name``, or an empty string."""
    match = re.search(rf"<input[^>]*name=\"{re.escape(name)}\"[^>]*>", page)
    return match.group(0) if match else ""


class TestPreferencesViewGet:
    def test_signed_out_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(PREFERENCES_URL)

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)

    def test_every_type_is_listed_against_every_channel_it_allows(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        names = {
            f"{kind.key}__{channel.key}"
            for kind in registry.get_all_types()
            for channel in registry.get_all_channels()
        }
        assert names
        assert all(toggle(page, name) for name in names)

    def test_a_choice_is_drawn_as_the_person_made_it(self, client, signed_in) -> None:
        NewFollower.disable_channel(signed_in, EmailChannel)
        NewFollower.enable_channel(signed_in, WebsiteChannel)

        page = client.get(PREFERENCES_URL).content.decode()

        assert "checked" not in toggle(page, "new_follower__email")
        assert "checked" in toggle(page, "new_follower__website")

    def test_a_required_choice_is_drawn_on_and_disabled(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        required = toggle(page, f"{SecurityNotice.key}__{EmailChannel.key}")
        assert "checked" in required
        assert "disabled" in required

    def test_with_no_types_registered_the_empty_state_is_drawn(
        self, client, signed_in, monkeypatch
    ) -> None:
        monkeypatch.setattr(registry, "_type_classes", {})

        page = client.get(PREFERENCES_URL).content.decode()

        assert "mvp-list-empty" in page
        assert toggle(page, "reply_received__website") == ""

    def test_the_browser_title_carries_the_views_page_title(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        title = re.search(r"<title>(.*?)</title>", page, re.S).group(1)
        assert str(PreferencesView.page_title) in title


def current_choices(user) -> dict[str, str]:
    """Return the form data that would save the person's choices unchanged."""
    return {
        f"{row['notification_type'].key}__{key}": "on"
        for row in get_notification_preferences(user)
        for key, choice in row["channels"].items()
        if choice["enabled"] and not choice["required"]
    }


class TestPreferencesViewPost:
    def test_signed_out_is_sent_to_sign_in(self, client, db) -> None:
        response = client.post(PREFERENCES_URL, {})

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)

    def test_a_type_turned_off_is_shown_off_and_every_other_choice_is_unchanged(
        self, client, signed_in
    ) -> None:
        before = client.get(PREFERENCES_URL).content.decode()
        data = current_choices(signed_in)
        data.pop("reply_received__website")

        client.post(PREFERENCES_URL, data)

        after = client.get(PREFERENCES_URL).content.decode()
        assert "checked" in toggle(before, "reply_received__website")
        assert "checked" not in toggle(after, "reply_received__website")
        unchanged = [name for name in data if name != "reply_received__website"]
        assert unchanged
        assert all(toggle(after, name) == toggle(before, name) for name in unchanged)

    def test_a_notification_of_a_turned_off_type_never_reaches_the_person(
        self, client, signed_in
    ) -> None:
        data = current_choices(signed_in)
        data.pop("reply_received__website")
        client.post(PREFERENCES_URL, data)

        send_notification(
            recipient=signed_in, notification_type=ReplyReceived, subject="Too late"
        )

        assert list(client.get(LIST_URL).context["page_obj"]) == []
        assert get_unread_count(signed_in) == 0

    def test_one_already_received_stays_listed_after_its_type_is_turned_off(
        self, client, signed_in, notification
    ) -> None:
        data = current_choices(signed_in)
        data.pop("reply_received__website")

        client.post(PREFERENCES_URL, data)

        assert list(client.get(LIST_URL).context["page_obj"]) == [notification]

    def test_saving_adds_a_success_message_and_goes_back_to_the_page(
        self, client, signed_in
    ) -> None:
        response = client.post(PREFERENCES_URL, current_choices(signed_in))

        assert response.status_code == 302
        assert response["Location"] == PREFERENCES_URL
        assert [m.level for m in get_messages(response.wsgi_request)] == [SUCCESS]


class TestPreferencesViewWithoutTheMailExtra:
    @pytest.fixture
    def without_mail(self, monkeypatch):
        channels = {
            key: channel
            for key, channel in registry._channel_classes.items()
            if key != "email"
        }
        monkeypatch.setattr(registry, "_channel_classes", channels)

    def test_only_the_site_channel_is_listed(
        self, client, signed_in, without_mail
    ) -> None:
        context = client.get(PREFERENCES_URL).context

        assert [channel.key for channel in context["channels"]] == ["website"]

    def test_no_choice_of_frequency_is_offered(
        self, client, signed_in, without_mail
    ) -> None:
        response = client.get(PREFERENCES_URL)

        assert response.context["frequencies"] == []
        assert "__frequency" not in response.content.decode()

    def test_with_the_mail_extra_the_frequencies_are_offered(
        self, client, signed_in
    ) -> None:
        response = client.get(PREFERENCES_URL)

        assert [key for key, _label in response.context["frequencies"]] == [
            "realtime",
            "daily",
            "weekly",
        ]
        assert "reply_received__frequency" in response.content.decode()


def frequency_select(page: str, type_key: str) -> str:
    """Return the select that chooses how often ``type_key`` arrives by email."""
    match = re.search(
        rf"<select[^>]*name=\"{re.escape(type_key)}__frequency\"[^>]*>.*?</select>",
        page,
        re.S,
    )
    return match.group(0) if match else ""


def frequency_of(user, type_key: str) -> str:
    """Return the frequency key the person has for ``type_key``."""
    return next(
        row["notification_frequency"]
        for row in get_notification_preferences(user)
        if row["notification_type"].key == type_key
    )


class TestPreferencesViewFrequency:
    def test_a_posted_frequency_is_stored_for_the_type(self, client, signed_in) -> None:
        data = current_choices(signed_in) | {"reply_received__frequency": "weekly"}

        client.post(PREFERENCES_URL, data)

        assert frequency_of(signed_in, "reply_received") == "weekly"
        assert (
            frequency_of(signed_in, "new_follower") == NewFollower.default_frequency.key
        )

    def test_the_frequency_is_stored_when_email_is_off(self, client, signed_in) -> None:
        data = current_choices(signed_in) | {"reply_received__frequency": "daily"}
        data.pop("reply_received__email", None)

        client.post(PREFERENCES_URL, data)

        assert frequency_of(signed_in, "reply_received") == "daily"

    def test_a_stored_frequency_is_drawn_selected(self, client, signed_in) -> None:
        client.post(
            PREFERENCES_URL,
            current_choices(signed_in) | {"reply_received__frequency": "weekly"},
        )

        select = frequency_select(
            client.get(PREFERENCES_URL).content.decode(), "reply_received"
        )

        assert re.findall(r'<option value="(\w+)" selected', select) == ["weekly"]

    def test_a_type_with_no_stored_choice_shows_its_declared_default(
        self, client, signed_in, monkeypatch
    ) -> None:
        class DigestFirst(NotificationType):
            key = "digest_first"
            name = "Digest first"
            default_frequency = DailyFrequency

        monkeypatch.setattr(
            registry,
            "_type_classes",
            {**registry._type_classes, DigestFirst.key: DigestFirst},
        )

        select = frequency_select(
            client.get(PREFERENCES_URL).content.decode(), DigestFirst.key
        )

        assert re.findall(r'<option value="(\w+)" selected', select) == ["daily"]

    def test_a_type_with_a_required_channel_offers_no_choice(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        assert f"{SecurityNotice.key}__frequency" not in page
        assert frequency_select(page, "reply_received")

    def test_the_row_keeps_the_choice_while_email_is_off(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        hidden = re.search(
            r'<input type="hidden" name="reply_received__frequency"[^>]*>', page
        ).group(0)
        assert 'x-bind:disabled="email"' in hidden
        assert 'x-bind:value="frequency"' in hidden
        assert 'x-bind:disabled="!email"' in frequency_select(page, "reply_received")


def unsubscribe_url(person, *notification_types):
    """The page address a link for these types leads to."""
    keys = [t.key for t in notification_types]
    return UnsubscribeLink.for_email(person, keys).path


def email_is_off(person, notification_type):
    return not any(
        c.key == "email" for c in notification_type.get_enabled_channels(person)
    )


ONE_CLICK = {"List-Unsubscribe": "One-Click"}


class TestUnsubscribeView:
    def test_a_visit_changes_nothing_and_asks_to_confirm(self, client, person) -> None:
        response = client.get(unsubscribe_url(person, ReplyReceived, NewFollower))

        assert response.context["outcome"] == "confirm"
        assert not email_is_off(person, ReplyReceived)
        assert not email_is_off(person, NewFollower)

    def test_the_page_turns_off_exactly_the_named_types(self, client, person) -> None:
        response = client.post(unsubscribe_url(person, ReplyReceived))

        assert response.context["outcome"] == "done"
        assert email_is_off(person, ReplyReceived)
        assert not email_is_off(person, NewFollower)
        assert any(
            c.key == "website" for c in ReplyReceived.get_enabled_channels(person)
        )

    def test_a_second_post_says_it_was_already_off(self, client, person) -> None:
        url = unsubscribe_url(person, ReplyReceived)
        client.post(url)

        assert client.post(url).context["outcome"] == "already"
        assert client.get(url).context["outcome"] == "already"

    def test_an_altered_link_is_invalid_for_a_visit_and_a_post(
        self, client, db
    ) -> None:
        url = "/notifications/unsubscribe/not-a-token/"

        assert client.get(url).context["outcome"] == "invalid"
        assert client.post(url).context["outcome"] == "invalid"

    def test_every_state_links_to_the_preferences_page(self, client, person) -> None:
        url = unsubscribe_url(person, ReplyReceived)
        pages = [
            client.get(url),
            client.post(url),
            client.post(url),
            client.get("/notifications/unsubscribe/not-a-token/"),
        ]

        assert [p.context["outcome"] for p in pages] == [
            "confirm",
            "done",
            "already",
            "invalid",
        ]
        for page in pages:
            assert f'href="{PREFERENCES_URL}"' in page.content.decode()

    def test_a_type_since_made_always_sent_is_left_on(self, client, person) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": [ReplyReceived.key, SecurityNotice.key]},
            salt=UNSUBSCRIBE_SALT,
        )
        url = reverse("mvp_community_notifications:unsubscribe", args=[token])

        client.post(url)

        assert email_is_off(person, ReplyReceived)
        assert not email_is_off(person, SecurityNotice)
        assert not NotificationTypeChannelPreference.objects.filter(
            user=person, notification_type=SecurityNotice.key
        ).exists()


class TestOneClickUnsubscribe:
    def test_it_answers_200_with_no_page_and_turns_email_off(
        self, client, person
    ) -> None:
        response = client.post(unsubscribe_url(person, ReplyReceived), ONE_CLICK)

        assert (response.status_code, response.content) == (200, b"")
        assert email_is_off(person, ReplyReceived)

    def test_an_invalid_link_answers_400(self, client, db) -> None:
        response = client.post("/notifications/unsubscribe/not-a-token/", ONE_CLICK)

        assert response.status_code == 400

    def test_a_link_with_only_always_sent_types_answers_400(
        self, client, person
    ) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": [SecurityNotice.key]}, salt=UNSUBSCRIBE_SALT
        )
        url = reverse("mvp_community_notifications:unsubscribe", args=[token])

        assert client.post(url, ONE_CLICK).status_code == 400


class TestUnsubscribeIsOpen:
    def test_a_signed_out_visitor_can_visit_and_post_without_a_csrf_token(
        self, person
    ) -> None:
        strict = Client(enforce_csrf_checks=True)
        url = unsubscribe_url(person, ReplyReceived)

        assert strict.get(url).status_code == 200
        assert strict.post(url).status_code == 200
        assert email_is_off(person, ReplyReceived)

    def test_it_stays_open_when_every_page_needs_sign_in(
        self, settings, client, person
    ) -> None:
        settings.MIDDLEWARE = [
            *settings.MIDDLEWARE,
            "django.contrib.auth.middleware.LoginRequiredMiddleware",
        ]
        url = unsubscribe_url(person, ReplyReceived)

        assert client.get(url).status_code == 200
        assert client.post(url).status_code == 200
        assert client.get(LIST_URL).status_code == 302
