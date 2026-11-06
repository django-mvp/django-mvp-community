"""The notifications extra's views, asserted as rendered through the demo."""

import re

from django.conf import settings
from django.contrib.messages import SUCCESS, get_messages
from django.db import connection
from django.shortcuts import resolve_url
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from generic_notifications import send_notification
from generic_notifications.channels import EmailChannel, WebsiteChannel
from generic_notifications.preferences import get_notification_preferences
from generic_notifications.registry import registry
from generic_notifications.utils import get_unread_count

from demo.notifications import NewFollower, ReplyReceived, SecurityNotice
from mvp_community.integrations.notifications.views import PreferencesView

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
