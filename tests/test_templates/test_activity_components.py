"""The activity components, rendered through a template string as a project places them."""

import html
import re
from urllib.parse import parse_qs, urlsplit

import pytest
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.factories import UserFactory

RECENT = "c-mvp_community.activity.recent"


def request_for(user, path="/"):
    request = RequestFactory().get(path)
    request.user = user
    return request


@pytest.fixture
def render_recent(render, person):
    def draw(attributes="", user=None, **context):
        context.setdefault("request", request_for(person if user is None else user))
        return render(f"<{RECENT} {attributes} />", **context)

    return draw


@pytest.fixture
def place_of_work(group):
    group.name = "Reading club"
    group.save()
    return group


class TestRecentActivityOfTheSite:
    def test_it_shows_public_activity_newest_first(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="joined", target=place_of_work, minutes_ago=30)
        make_action(person, verb="finished", target=place_of_work, minutes_ago=5)

        markup = render_recent()

        assert markup.index("finished") < markup.index("joined")

    def test_it_leaves_out_activity_that_is_not_public(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="whispered", target=place_of_work, public=False)

        assert "whispered" not in render_recent()

    def test_it_is_the_same_for_a_signed_out_visitor(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="finished", target=place_of_work)

        assert "finished" in render_recent(user=AnonymousUser())

    def test_it_leaves_out_activity_whose_target_was_deleted(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="finished", target=place_of_work)
        place_of_work.delete()

        assert "finished" not in render_recent()

    def test_it_escapes_what_the_model_data_holds(
        self, render_recent, person, make_action
    ) -> None:
        hostile = Group.objects.create(name="<script>alert(1)</script>")
        make_action(person, verb="<b>finished</b>", target=hostile)

        markup = render_recent()

        assert "<script>alert(1)</script>" not in markup
        assert "<b>finished</b>" not in markup


class TestRecentActivityAroundAnObject:
    def test_it_shows_activity_where_the_object_acted_was_acted_on_or_was_the_place(
        self, render_recent, person, group, make_action
    ) -> None:
        other = Group.objects.create(name="Elsewhere")
        make_action(group, verb="acted", target=person)
        make_action(person, verb="visited", target=group)
        make_action(person, verb="unrelated", target=other)

        markup = render_recent(':object="group"', group=group)

        assert "acted" in markup
        assert "visited" in markup
        assert "unrelated" not in markup

    def test_it_leaves_out_activity_that_is_not_public(
        self, render_recent, person, group, make_action
    ) -> None:
        make_action(person, verb="whispered", target=group, public=False)

        assert "whispered" not in render_recent(':object="group"', group=group)


class TestRecentActivityOfWhatAPersonFollows:
    def test_it_shows_only_what_the_signed_in_person_follows(
        self, render_recent, person, place_of_work, make_action, make_follow
    ) -> None:
        followed = UserFactory(first_name="Anna", last_name="Weber")
        stranger = UserFactory(first_name="Zed", last_name="Zimmer")
        make_follow(person, followed)
        make_action(followed, verb="finished", target=place_of_work)
        make_action(stranger, verb="stumbled", target=place_of_work)

        markup = render_recent("following")

        assert "finished" in markup
        assert "stumbled" not in markup

    def test_it_leaves_out_the_persons_own_actions(
        self, render_recent, person, place_of_work, make_action, make_follow
    ) -> None:
        make_follow(person, place_of_work)
        make_action(person, verb="stumbled", target=place_of_work)

        assert "stumbled" not in render_recent("following")

    def test_it_shows_nothing_to_a_signed_out_visitor(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="finished", target=place_of_work)

        markup = render_recent("following", user=AnonymousUser())

        assert "finished" not in markup
        assert "Nothing has happened yet" in markup


class TestRecentActivityKinds:
    def test_a_verb_limits_it_to_that_kind(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        make_action(person, verb="finished", target=place_of_work)
        make_action(person, verb="joined", target=place_of_work)

        markup = render_recent('verb="finished"')

        assert "finished" in markup
        assert "joined" not in markup


class TestRecentActivityLimit:
    def test_the_limit_caps_the_rows(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        for minutes in range(5):
            make_action(
                person, verb=f"did{minutes}", target=place_of_work, minutes_ago=minutes
            )

        markup = render_recent('limit="3"')

        assert [
            verb in markup for verb in ("did0", "did1", "did2", "did3", "did4")
        ] == [
            True,
            True,
            True,
            False,
            False,
        ]

    def test_it_links_to_the_full_list_when_there_is_more(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        for minutes in range(3):
            make_action(person, target=place_of_work, minutes_ago=minutes)

        markup = render_recent('limit="2" more_url="/everything/"')

        assert 'href="/everything/"' in markup

    def test_it_has_no_link_when_nothing_more_is_left(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        for minutes in range(2):
            make_action(person, target=place_of_work, minutes_ago=minutes)

        assert "/everything/" not in render_recent('limit="2" more_url="/everything/"')

    def test_it_has_no_link_without_an_address(
        self, render_recent, person, place_of_work, make_action
    ) -> None:
        for minutes in range(3):
            make_action(person, target=place_of_work, minutes_ago=minutes)

        assert "View all activity" not in render_recent('limit="2"')


class TestRecentActivityEmpty:
    def test_it_says_so_when_there_is_nothing_to_show(self, render_recent) -> None:
        assert "Nothing has happened yet" in render_recent()


class TestActivityName:
    NAME = "c-mvp_community.activity.name"

    def test_a_model_with_an_address_is_a_link(self, render, group) -> None:
        group.get_absolute_url = lambda: "/groups/1/"

        markup = render(f'<{self.NAME} :object="group" />', group=group)

        assert 'href="/groups/1/"' in markup

    def test_a_model_without_an_address_is_plain_text(self, render) -> None:
        class Place:
            def __str__(self):
                return "A place"

        markup = render(f'<{self.NAME} :object="place" />', place=Place())

        assert "A place" in markup
        assert "<a " not in markup


class TestFollowersList:
    FOLLOWERS = "c-mvp_community.activity.followers"

    def following(self, group, make_follow, count):
        people = [
            UserFactory(first_name=f"Follower{n:02d}", last_name="Fan")
            for n in range(count)
        ]
        for follower in people:
            make_follow(follower, group)
        return people

    def drawn(self, markup, people):
        return [p for p in people if p.first_name in markup]

    def test_it_shows_how_many_follow(self, render, group, make_follow) -> None:
        self.following(group, make_follow, 3)

        assert "3 followers" in render(
            f'<{self.FOLLOWERS} :object="group" />', group=group
        )

    def test_it_lists_the_followers(self, render, group, make_follow) -> None:
        people = self.following(group, make_follow, 3)

        markup = render(f'<{self.FOLLOWERS} :object="group" />', group=group)

        assert self.drawn(markup, people) == people

    def test_it_lists_eight_and_says_how_many_more(
        self, render, group, make_follow
    ) -> None:
        people = self.following(group, make_follow, 11)

        markup = render(f'<{self.FOLLOWERS} :object="group" />', group=group)

        assert len(self.drawn(markup, people)) == 8
        assert "3 more" in markup

    def test_one_past_eight_says_one_more(self, render, group, make_follow) -> None:
        self.following(group, make_follow, 9)

        assert "1 more" in render(f'<{self.FOLLOWERS} :object="group" />', group=group)

    def test_it_says_nothing_more_when_eight_or_fewer_follow(
        self, render, group, make_follow
    ) -> None:
        self.following(group, make_follow, 8)

        markup = render(f'<{self.FOLLOWERS} :object="group" />', group=group)

        assert " more" not in markup

    def test_counting_asks_one_question(self, render, group, make_follow) -> None:
        self.following(group, make_follow, 11)

        with CaptureQueriesContext(connection) as queries:
            render(f'<{self.FOLLOWERS} :object="group" />', group=group)

        assert sum("COUNT(" in query["sql"] for query in queries) == 1
        assert len(queries) == 2

    def test_nobody_following_draws_no_rows(self, render, group) -> None:
        markup = render(f'<{self.FOLLOWERS} :object="group" />', group=group)

        assert "<li" not in markup

    def test_plain_leaves_out_the_heading(self, render, group, make_follow) -> None:
        self.following(group, make_follow, 2)

        with_heading = render(f'<{self.FOLLOWERS} :object="group" />', group=group)
        plain = render(f'<{self.FOLLOWERS} :object="group" plain />', group=group)

        assert "2 followers" in with_heading
        assert "2 followers" not in plain


class TestFollowControl:
    FOLLOW = "c-mvp_community.activity.follow"

    @pytest.fixture
    def draw(self, render, person):
        def draw_control(attributes="", user=None, **context):
            who = person if user is None else user
            context.setdefault("request", request_for(who))
            context.setdefault("user", who)
            return render(f"<{self.FOLLOW} {attributes} />", **context)

        return draw_control

    def address(self, name, obj, query=""):
        return (
            reverse(name, args=[ContentType.objects.get_for_model(obj).pk, obj.pk])
            + query
        )

    def attribute(self, markup, name):
        return html.unescape(re.search(rf'{name}="([^"]*)"', markup).group(1))

    def test_it_posts_to_the_follow_address_when_not_following(
        self, draw, group
    ) -> None:
        markup = draw(':object="group"', group=group)

        assert self.attribute(markup, "action").startswith(
            self.address("actstream_follow_all", group)
        )

    def test_it_posts_to_the_stop_following_address_when_following(
        self, draw, person, group, make_follow
    ) -> None:
        make_follow(person, group)

        markup = draw(':object="group"', group=group)

        assert self.attribute(markup, "action").startswith(
            self.address("actstream_unfollow", group)
        )

    def test_it_shows_how_many_follow(self, draw, group, make_follow) -> None:
        make_follow(UserFactory(), group)
        make_follow(UserFactory(), group)

        words = re.sub(r"<[^>]+>", " ", draw(':object="group"', group=group)).split()

        assert "2" in words

    def test_a_signed_out_visitor_gets_a_link_to_sign_in_carrying_next(
        self, draw, group
    ) -> None:
        markup = draw(
            ':object="group" next="/lessons/3/"', user=AnonymousUser(), group=group
        )

        assert "<form" not in markup
        assert f'href="{reverse("account_login")}?next=/lessons/3/"' in markup

    def test_a_person_s_own_control_has_the_count_and_no_form(self, draw, person):
        markup = draw(':object="person"', person=person)

        assert "<form" not in markup
        assert "data-follow-control" in markup

    def test_the_wrapper_is_the_one_element_htmx_replaces(self, draw, group) -> None:
        markup = draw(':object="group"', group=group)

        assert len(re.findall(r"<div[^>]*data-follow-control", markup)) == 1
        assert self.attribute(markup, "hx-swap") == "outerHTML"
        assert "hx-boost" not in markup

    def test_htmx_posts_to_the_follow_address_and_asks_for_the_control_back(
        self, draw, group
    ) -> None:
        markup = draw(':object="group" next="/lessons/3/"', group=group)

        posted = urlsplit(self.attribute(markup, "hx-post"))
        refresh = urlsplit(parse_qs(posted.query)["next"][0])

        assert posted.path == self.address("actstream_follow_all", group)
        assert refresh.path == self.address(
            "mvp_community_activity:follow_control", group
        )
        assert parse_qs(refresh.query)["next"] == ["/lessons/3/"]

    def test_replace_row_makes_the_row_the_target_and_removes_it(
        self, draw, group
    ) -> None:
        markup = draw(':object="group" replace_row', group=group)

        assert self.attribute(markup, "hx-target") == "closest [data-follow-row]"
        assert self.attribute(markup, "hx-swap") == "delete"

    def test_the_plain_form_returns_to_the_page(self, draw, group) -> None:
        markup = draw(':object="group" next="/lessons/3/"', group=group)

        action = urlsplit(self.attribute(markup, "action"))

        assert parse_qs(action.query)["next"] == ["/lessons/3/"]

    def test_next_defaults_to_the_current_page(self, draw, person, group) -> None:
        markup = draw(
            ':object="group"', group=group, request=request_for(person, "/lessons/3/")
        )

        action = urlsplit(self.attribute(markup, "action"))

        assert parse_qs(action.query)["next"] == ["/lessons/3/"]

    def test_the_form_carries_the_csrf_token(self, draw, group) -> None:
        markup = draw(':object="group"', group=group, csrf_token="a-token")

        assert 'name="csrfmiddlewaretoken"' in markup

    def test_following_through_the_follow_address_and_the_control_route(
        self, client, signed_in, group, make_follow
    ) -> None:
        make_follow(UserFactory(), group)
        follow = self.address(
            "actstream_follow_all",
            group,
            "?next=" + self.address("mvp_community_activity:follow_control", group),
        )

        followed = client.post(follow, follow=True)
        stopped = client.post(
            self.address(
                "actstream_unfollow",
                group,
                "?next=" + self.address("mvp_community_activity:follow_control", group),
            ),
            follow=True,
        )

        assert self.address("actstream_unfollow", group) in followed.content.decode()
        assert "2" in re.sub(r"<[^>]+>", " ", followed.content.decode()).split()
        assert self.address("actstream_follow_all", group) in stopped.content.decode()
        assert "1" in re.sub(r"<[^>]+>", " ", stopped.content.decode()).split()
