"""A project replaces one template or component of the notifications pages by shipping its own."""

import copy
from pathlib import Path

import pytest
from django.urls import reverse

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
