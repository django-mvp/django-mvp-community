"""The activity extra's views, asserted as rendered through the demo."""

import re
from datetime import timedelta

import pytest
from actstream.actions import unfollow
from actstream.models import Action, Follow
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from tests.factories import GroupFactory, UserFactory

SITE_URL = reverse("site_activity")
FEED_URL = reverse("feed")


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


class TestActivityFeedViewOfWhatAPersonFollows:
    def test_a_signed_out_visitor_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(FEED_URL)

        assert response.status_code == 302
        assert response["Location"].startswith(reverse("account_login"))

    def test_it_lists_public_activity_of_what_the_person_follows_newest_first(
        self, client, signed_in, group, make_action, make_follow
    ) -> None:
        other = UserFactory()
        make_follow(signed_in, group)
        make_follow(signed_in, other)
        older = make_action(other, target=group, minutes_ago=30)
        newer = make_action(other, verb="joined", target=GroupFactory(), minutes_ago=5)

        assert listed(client.get(FEED_URL)) == [newer, older]

    def test_it_lists_nothing_else(
        self, client, signed_in, group, make_action, make_follow
    ) -> None:
        stranger = UserFactory()
        make_follow(signed_in, group)
        make_action(stranger, target=GroupFactory())
        make_action(stranger, target=group, public=False)

        assert listed(client.get(FEED_URL)) == []

    def test_it_never_lists_the_person_s_own_activity(
        self, client, signed_in, group, make_action, make_follow
    ) -> None:
        make_follow(signed_in, group)
        make_action(signed_in, target=group)

        assert listed(client.get(FEED_URL)) == []

    def test_after_unfollowing_new_activity_of_that_person_is_left_out(
        self, client, signed_in, make_action, make_follow
    ) -> None:
        other = UserFactory()
        make_follow(signed_in, other)
        unfollow(signed_in, other)
        make_action(other, verb="finished")

        assert listed(client.get(FEED_URL)) == []

    def test_following_someone_records_a_public_action_the_followers_own_feed_omits(
        self, client, signed_in, person
    ) -> None:
        other = UserFactory()

        client.post(
            reverse("actstream_follow_all", args=[_content_type_id(other), other.pk])
        )

        started = Action.objects.get(verb="started following")
        assert (started.actor, started.target, started.public) == (person, other, True)
        assert listed(client.get(FEED_URL)) == []

    def test_someone_who_follows_the_follower_sees_that_they_started_following(
        self, client, signed_in, person, make_follow
    ) -> None:
        other, admirer = UserFactory(), UserFactory()
        make_follow(admirer, person)
        client.post(
            reverse("actstream_follow_all", args=[_content_type_id(other), other.pk])
        )
        client.force_login(admirer)

        assert [a.verb for a in listed(client.get(FEED_URL))] == ["started following"]

    def test_following_nothing_draws_the_empty_state(self, client, signed_in) -> None:
        response = client.get(FEED_URL)

        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 0

    def test_twenty_to_a_page_and_the_rest_on_page_two(
        self, client, signed_in, group, make_action, make_follow
    ) -> None:
        make_follow(signed_in, group)
        other = UserFactory()
        for minutes in range(25):
            make_action(other, target=group, minutes_ago=minutes)

        first = client.get(FEED_URL)
        second = client.get(FEED_URL, {"page": 2})

        assert (len(listed(first)), len(listed(second))) == (20, 5)

    def test_it_asks_the_same_number_of_questions_for_one_action_or_many(
        self, client, signed_in, make_action, make_follow
    ) -> None:
        other = UserFactory()
        make_follow(signed_in, other)

        def queries_with(actions: int) -> int:
            for _ in range(actions):
                make_action(other, target=GroupFactory())
            with CaptureQueriesContext(connection) as queries:
                client.get(FEED_URL)
            return len(queries)

        client.get(FEED_URL)

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


class TestFollowControlView:
    def address(self, obj, query=None):
        address = reverse(
            "mvp_community_activity:follow_control",
            args=[ContentType.objects.get_for_model(obj).pk, obj.pk],
        )
        return f"{address}?{query}" if query else address

    def test_a_signed_out_request_is_sent_to_sign_in(self, client, group) -> None:
        response = client.get(self.address(group))

        assert response.status_code == 302
        assert response["Location"].startswith(reverse("account_login"))

    def test_it_draws_the_control_alone(self, client, signed_in, group) -> None:
        response = client.get(self.address(group))

        content = response.content.decode()
        assert response.status_code == 200
        assert "data-follow-control" in content
        assert "<html" not in content

    def test_it_shows_unfollow_once_followed(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(signed_in, group)

        content = client.get(self.address(group)).content.decode()

        assert (
            reverse(
                "actstream_unfollow",
                args=[_content_type_id(group), group.pk],
            )
            in content
        )

    def test_it_is_get_only(self, client, signed_in, group) -> None:
        assert client.post(self.address(group)).status_code == 405

    def test_an_unknown_type_is_not_found(self, client, signed_in) -> None:
        address = reverse("mvp_community_activity:follow_control", args=[999999, "1"])

        assert client.get(address).status_code == 404

    def test_an_unknown_object_is_not_found(self, client, signed_in, group) -> None:
        address = reverse(
            "mvp_community_activity:follow_control",
            args=[_content_type_id(group), "999999"],
        )

        assert client.get(address).status_code == 404

    def test_an_object_that_is_not_a_number_is_not_found(
        self, client, signed_in, group
    ) -> None:
        address = reverse(
            "mvp_community_activity:follow_control",
            args=[_content_type_id(group), "not-a-number"],
        )

        assert client.get(address).status_code == 404

    def test_a_model_not_registered_with_django_activity_stream_is_not_found(
        self, client, signed_in
    ) -> None:
        permission = Permission.objects.first()

        assert client.get(self.address(permission)).status_code == 404

    def test_a_local_next_is_where_the_plain_form_returns_to(
        self, client, signed_in, group
    ) -> None:
        content = client.get(self.address(group, "next=/lessons/3/")).content.decode()

        assert "next=/lessons/3/" in content

    @pytest.mark.parametrize(
        "next_address", ["https://evil.example/steal", "//evil.example/steal"]
    )
    def test_an_off_site_next_is_replaced_by_nothing(
        self, client, signed_in, group, next_address
    ) -> None:
        content = client.get(
            self.address(group, f"next={next_address}")
        ).content.decode()

        assert "evil.example" not in content


class TestFollowingView:
    URL = reverse("mvp_community_activity:following")

    def test_a_signed_out_visitor_is_sent_to_sign_in(self, client, db) -> None:
        response = client.get(self.URL)

        assert response.status_code == 302
        assert response["Location"].startswith(reverse("account_login"))

    def test_it_lists_everything_the_person_follows_newest_first(
        self, client, signed_in, group, make_follow
    ) -> None:
        other = UserFactory()
        older = make_follow(signed_in, group)
        newer = make_follow(signed_in, other)
        Follow.objects.filter(pk=older.pk).update(
            started=timezone.now() - timedelta(days=1)
        )

        assert listed(client.get(self.URL)) == [newer, older]

    def test_it_leaves_out_what_other_people_follow(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(UserFactory(), group)

        assert listed(client.get(self.URL)) == []

    def test_each_row_links_to_the_page_of_what_is_followed(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(signed_in, group)

        content = client.get(self.URL).content.decode()

        assert f'href="{reverse("group", args=[group.pk])}"' in content

    def test_each_row_has_a_control_offering_to_stop_following(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(signed_in, group)

        content = client.get(self.URL).content.decode()

        assert (
            reverse("actstream_unfollow", args=[_content_type_id(group), group.pk])
            in content
        )

    def test_stopping_following_through_the_control_removes_the_row(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(signed_in, group)
        content = client.get(self.URL).content.decode()
        row = re.search(r"<li[^>]*data-follow-row[^>]*>", content)
        control = re.search(r"<form[^>]*hx-post[^>]*>", content).group(0)
        assert row is not None
        assert 'hx-target="closest [data-follow-row]"' in control
        assert 'hx-swap="delete"' in control

        client.post(
            reverse("actstream_unfollow", args=[_content_type_id(group), group.pk]),
            follow=True,
        )

        assert listed(client.get(self.URL)) == []

    def test_following_nothing_draws_the_empty_state(self, client, signed_in) -> None:
        response = client.get(self.URL)

        assert response.status_code == 200
        assert response.context["page_obj"].paginator.count == 0
        assert "data-follow-row" not in response.content.decode()

    def test_twenty_to_a_page_and_the_rest_on_page_two(
        self, client, signed_in, make_follow
    ) -> None:
        for _ in range(25):
            make_follow(signed_in, GroupFactory())

        first = client.get(self.URL)
        second = client.get(self.URL, {"page": 2})

        assert (len(listed(first)), len(listed(second))) == (20, 5)


def _content_type_id(obj) -> int:
    return ContentType.objects.get_for_model(obj).pk
