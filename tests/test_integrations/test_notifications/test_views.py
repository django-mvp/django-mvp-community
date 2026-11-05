"""The notifications extra's views, asserted as rendered through the demo."""

from django.conf import settings
from django.db import connection
from django.shortcuts import resolve_url
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

SIGN_IN_URL = resolve_url(settings.LOGIN_URL)
LIST_URL = reverse("mvp_community_notifications:list")


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
