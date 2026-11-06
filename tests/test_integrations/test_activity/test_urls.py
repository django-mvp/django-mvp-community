"""The routes the activity extra adds: its own page and django-activity-stream's follow routes."""

import pytest
from django.urls import NoReverseMatch, resolve, reverse

import mvp_community.integrations.activity.urls as activity_urls

FOLLOW_ROUTES = [
    "actstream_follow",
    "actstream_follow_all",
    "actstream_unfollow",
    "actstream_unfollow_all",
]


def address_of(name: str, person) -> str:
    from django.contrib.contenttypes.models import ContentType

    return reverse(name, args=[ContentType.objects.get_for_model(person).pk, person.pk])


class TestFollowRoutes:
    @pytest.mark.parametrize("name", FOLLOW_ROUTES)
    def test_each_follow_route_resolves_under_activity(self, name, person) -> None:
        assert address_of(name, person).startswith("/activity/")

    @pytest.mark.parametrize("name", FOLLOW_ROUTES)
    def test_each_follow_route_is_django_activity_streams_own(
        self, name, person
    ) -> None:
        from actstream import views

        assert resolve(address_of(name, person)).func is views.follow_unfollow

    def test_the_following_page_has_a_route_under_the_account_center(self) -> None:
        assert (
            reverse("mvp_community_activity:following") == "/account-center/following/"
        )

    def test_there_is_no_feed_route(self) -> None:
        with pytest.raises(NoReverseMatch):
            reverse("mvp_community_activity:feed")

    def test_only_the_follow_routes_and_the_following_page_are_mounted(self) -> None:
        # actstream.urls also mounts a detail page that shows actions which are
        # not public and a page that lists anyone's follows to anyone.
        names = set()
        for pattern in activity_urls.urlpatterns:
            names |= {getattr(inner, "name", None) for inner in _flatten(pattern)}

        assert names - {None} == {*FOLLOW_ROUTES, "following"}

    def test_an_action_that_is_not_public_has_no_page(
        self, client, signed_in, person, make_action
    ) -> None:
        private = make_action(person, public=False)

        assert client.get(f"/activity/detail/{private.pk}/").status_code == 404

    def test_what_a_person_follows_is_not_listed_to_others(
        self, client, person, group, make_follow
    ) -> None:
        make_follow(person, group)

        assert client.get(f"/activity/following/{person.pk}/").status_code == 404


def _flatten(pattern):
    inner = getattr(pattern, "url_patterns", None)
    if inner is None:
        return [pattern]
    return [leaf for child in inner for leaf in _flatten(child)]
