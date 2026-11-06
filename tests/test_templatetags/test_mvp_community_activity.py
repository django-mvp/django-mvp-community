"""The followers tag, rendered as a template uses it."""

from django.db import connection
from django.template import Context, Template
from django.test.utils import CaptureQueriesContext

from tests.factories import UserFactory

SOURCE = "{% load mvp_community_activity %}{% followers_of obj as people %}"


def render_with(obj, body: str) -> str:
    return Template(SOURCE + body).render(Context({"obj": obj}))


class TestFollowersOf:
    def test_it_gives_the_people_who_follow_the_object(
        self, person, group, make_follow
    ) -> None:
        other = UserFactory()
        make_follow(person, group)
        make_follow(other, group)

        markup = render_with(group, "{% for p in people %}{{ p.pk }},{% endfor %}")

        assert sorted(markup.strip(",").split(",")) == sorted(
            [str(person.pk), str(other.pk)]
        )

    def test_it_counts_the_follows_of_that_object_only(
        self, person, group, make_follow
    ) -> None:
        make_follow(person, group)
        make_follow(UserFactory(), group)
        make_follow(person, UserFactory())

        assert render_with(group, "{{ people.count }}") == "2"

    def test_it_counts_nobody_for_an_object_nobody_follows(self, group) -> None:
        assert render_with(group, "{{ people.count }}") == "0"

    def test_counting_asks_one_question(self, person, group, make_follow) -> None:
        for follower in (person, UserFactory(), UserFactory()):
            make_follow(follower, group)

        with CaptureQueriesContext(connection) as queries:
            render_with(group, "{{ people.count }}")

        assert len(queries) == 1
