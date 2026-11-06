"""A project replaces one template or component of the notifications pages by shipping its own."""

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from tests.factories import GroupFactory, UserFactory

OVERRIDES = Path(__file__).resolve().parent.parent / "templates" / "overrides"

LIST_URL = reverse("mvp_community_notifications:list")
PREFERENCES_URL = reverse("mvp_community_notifications:preferences")
ACCOUNT_CENTER_URL = reverse("account-center")


@pytest.fixture
def override(settings):
    """Put one override directory ahead of the package's templates."""

    def use(name: str) -> None:
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [*templates[0]["DIRS"], OVERRIDES / name]
        settings.TEMPLATES = templates

    return use


class TestNotificationRowOverride:
    def test_the_project_row_replaces_the_packages(
        self, client, signed_in, make_notifications, override
    ) -> None:
        make_notifications(3)
        override("row")

        page = client.get(LIST_URL).content.decode()

        assert page.count('data-override="row"') == 3

    def test_the_rest_of_the_page_is_drawn_as_before(
        self, client, signed_in, make_notifications, override
    ) -> None:
        make_notifications(1)
        override("row")

        page = client.get(LIST_URL).content.decode()

        assert reverse("mvp_community_notifications:mark_all_read") in page
        assert 'id="mvp-community-bell"' in page


class TestPreferencesCardOverride:
    def test_the_project_card_replaces_the_packages(
        self, client, signed_in, override
    ) -> None:
        override("card")

        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        assert 'data-override="card"' in page
        assert PREFERENCES_URL not in page.split('id="account-center-cards"', 1)[1]

    def test_the_rest_of_the_page_is_drawn_as_before(
        self, client, signed_in, override
    ) -> None:
        override("card")

        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        assert PREFERENCES_URL in page.split('id="account-center-cards"', 1)[0]


class TestPreferencesPageOverride:
    def test_the_project_page_replaces_the_packages(
        self, client, signed_in, override
    ) -> None:
        override("page")

        page = client.get(PREFERENCES_URL).content.decode()

        assert 'data-override="page"' in page
        assert "reply_received__website" not in page

    def test_the_rest_of_the_feature_is_drawn_as_before(
        self, client, signed_in, override
    ) -> None:
        override("page")

        shell = client.get(LIST_URL).content.decode()
        account_center = client.get(ACCOUNT_CENTER_URL).content.decode()

        assert 'id="mvp-community-bell"' in shell
        assert PREFERENCES_URL in account_center


@pytest.fixture
def scene(signed_in, group, make_action, make_follow):
    """A group with one public activity and one follower, seen by a signed-in person."""
    actor = UserFactory(first_name="Anna", last_name="Weber")
    follower = UserFactory(first_name="Follower", last_name="Fan")
    followed = GroupFactory()
    make_action(actor, verb="finished", target=group)
    make_follow(follower, group)
    make_follow(signed_in, followed)
    follow_address = reverse(
        "actstream_follow_all",
        args=[ContentType.objects.get_for_model(group).pk, group.pk],
    )
    return SimpleNamespace(
        group_page=reverse("group", args=[group.pk]),
        site_page=reverse("site_activity"),
        following_page=reverse("mvp_community_activity:following"),
        account_center=reverse("account-center"),
        verb="finished",
        follow_address=follow_address,
        actor_link=f'href="/people/{actor.pk}/"',
        follower_link=f'href="/people/{follower.pk}/"',
        followed_link=f'href="/groups/{followed.pk}/"',
    )


# Each template: the page it shows on and what only it draws there, then a page
# and a marker that show the rest of the feature is as before.
ACTIVITY_OVERRIDES = {
    "activity_recent": ("group_page", "verb", "group_page", "follow_address"),
    "activity_feed_component": ("group_page", "verb", "group_page", "follow_address"),
    "activity_entry": ("group_page", "verb", "group_page", "follow_address"),
    "activity_name": ("group_page", "actor_link", "group_page", "follow_address"),
    "activity_follow": ("group_page", "follow_address", "group_page", "verb"),
    "activity_followers": ("group_page", "follower_link", "group_page", "verb"),
    "activity_following_card": (
        "account_center",
        "following_page",
        "account_center",
        "following_page",
    ),
    "activity_feed_page": ("site_page", "verb", "group_page", "verb"),
    "activity_following_page": (
        "following_page",
        "followed_link",
        "account_center",
        "following_page",
    ),
}


def drawn_by_the_page(markup: str) -> str:
    """Return the page without the Account Center's sidebar, which links the following page."""
    return markup.split('id="account-center-cards"')[-1]


class TestActivityTemplateOverride:
    @pytest.mark.parametrize("name", ACTIVITY_OVERRIDES)
    def test_the_project_template_replaces_the_packages(
        self, name, client, scene, override
    ) -> None:
        page_name, marker_name, _, _ = ACTIVITY_OVERRIDES[name]
        page, marker = getattr(scene, page_name), getattr(scene, marker_name)
        # The package's template draws the marker to begin with, or its absence
        # below proves nothing.
        assert marker in drawn_by_the_page(client.get(page).content.decode())
        override(name)

        replaced = drawn_by_the_page(client.get(page).content.decode())

        assert f'data-override="{name}"' in replaced
        assert marker not in replaced

    @pytest.mark.parametrize("name", ACTIVITY_OVERRIDES)
    def test_the_rest_of_the_feature_is_drawn_as_before(
        self, name, client, scene, override
    ) -> None:
        _, _, page_name, marker_name = ACTIVITY_OVERRIDES[name]
        override(name)

        kept = client.get(getattr(scene, page_name)).content.decode()

        assert getattr(scene, marker_name) in kept
