"""The activity extra's views, asserted as rendered through the demo."""

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.factories import GroupFactory

SITE_URL = reverse("site_activity")


def listed(response) -> list:
    return list(response.context["page_obj"])


class TestActivityFeedViewOfTheSite:
    def test_it_lists_public_activity_newest_first(
        self, client, person, group, make_action
    ) -> None:
        older = make_action(person, target=group, minutes_ago=30)
        newer = make_action(person, target=group, minutes_ago=5)

        assert listed(client.get(SITE_URL)) == [newer, older]

    def test_it_is_open_to_a_signed_out_visitor(
        self, client, person, group, make_action
    ) -> None:
        make_action(person, target=group)

        assert client.get(SITE_URL).status_code == 200

    def test_it_leaves_out_activity_that_is_not_public(
        self, client, person, group, make_action
    ) -> None:
        shown = make_action(person, target=group)
        make_action(person, target=group, public=False)

        assert listed(client.get(SITE_URL)) == [shown]

    def test_twenty_to_a_page_and_the_rest_on_page_two(
        self, client, person, group, make_action
    ) -> None:
        for minutes in range(25):
            make_action(person, target=group, minutes_ago=minutes)

        first = client.get(SITE_URL)
        second = client.get(SITE_URL, {"page": 2})

        assert (len(listed(first)), len(listed(second))) == (20, 5)

    def test_a_verb_limits_it_to_that_kind(
        self, client, person, group, make_action
    ) -> None:
        finished = make_action(person, verb="finished", target=group)
        make_action(person, verb="joined", target=group)

        response = client.get(reverse("finished_activity"))

        assert listed(response) == [finished]

    def test_it_asks_the_same_number_of_questions_for_one_action_or_many(
        self, client, person, make_action
    ) -> None:
        def queries_with(actions: int) -> int:
            for _ in range(actions):
                make_action(person, target=GroupFactory())
            with CaptureQueriesContext(connection) as queries:
                client.get(SITE_URL)
            return len(queries)

        # The first page drawn fills Django's content type cache.
        client.get(SITE_URL)

        assert queries_with(1) == queries_with(5)


class TestActivityFeedViewOfOneObject:
    def test_it_lists_only_activity_around_the_object(
        self, client, person, group, make_action
    ) -> None:
        around = make_action(person, target=group)
        make_action(person, target=GroupFactory())

        response = client.get(reverse("group_activity", args=[group.pk]))

        assert listed(response) == [around]

    def test_without_an_object_it_is_a_configuration_error(self, client, db) -> None:
        with pytest.raises(ImproperlyConfigured):
            client.get(reverse("unconfigured_object_activity"))


class TestActivityFeedViewMisconfigured:
    def test_a_stream_that_is_not_one_of_the_three_is_a_configuration_error(
        self, client, db
    ) -> None:
        with pytest.raises(ImproperlyConfigured):
            client.get(reverse("unknown_stream_activity"))
