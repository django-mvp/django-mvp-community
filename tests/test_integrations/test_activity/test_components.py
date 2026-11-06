"""The activity components, rendered through a template string as a project places them."""

import pytest
from django.contrib.auth.models import AnonymousUser, Group
from django.test import RequestFactory

from tests.factories import UserFactory

RECENT = "c-mvp_community.activity.recent"


def request_for(user):
    request = RequestFactory().get("/")
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
