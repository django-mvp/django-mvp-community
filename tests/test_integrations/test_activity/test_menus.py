"""The Account Center entry, and the absence of any entry of the package's own in the sidebar."""

import re
import subprocess
import sys
import types

from django.test import override_settings
from django.urls import reverse

from mvp_community.integrations.activity import urls as activity_urls
from tests import urls as project_urls

ACCOUNT_CENTER_URL = reverse("account-center")
FOLLOWING_URL = reverse("mvp_community_activity:following")
CARDS_ID = 'id="account-center-cards"'

# A fresh interpreter, so what the suite imported cannot stand in for a project
# that has or lacks the extra.
LIST_MENU_ENTRIES = """
import sys

import django
from django.conf import settings

apps = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sites"]
apps += ["mvp_community", "mvp", "flex_menu"] + sys.argv[1:]
settings.configure(INSTALLED_APPS=apps, SITE_ID=1)
django.setup()

from mvp.menus import AccountCenterMenu, AppMenu

print([child.name for child in AppMenu.children])
print([child.name for child in AccountCenterMenu.children])
"""


def menu_entries_with(*extra_apps: str) -> tuple[list[str], list[str]]:
    result = subprocess.run(  # noqa: S603 - fixed script, this interpreter
        [sys.executable, "-c", LIST_MENU_ENTRIES, *extra_apps],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    sidebar, account_center = result.stdout.strip().splitlines()
    return eval(sidebar), eval(account_center)  # noqa: S307 - lists of names we printed


def links_in(markup: str) -> list[str]:
    return re.findall(r'<a[^>]*href="([^"]*)"', markup)


class TestAccountCenterEntry:
    def test_the_sidebar_links_to_the_following_page(self, client, signed_in) -> None:
        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        sidebar = page.split(CARDS_ID, 1)[0]
        assert FOLLOWING_URL in links_in(sidebar)

    def test_the_extra_adds_the_entry_to_the_account_center(self) -> None:
        _, account_center = menu_entries_with("actstream")

        assert "following" in account_center

    def test_without_the_extra_there_is_no_entry(self) -> None:
        _, account_center = menu_entries_with()

        assert "following" not in account_center


class TestFollowingCard:
    def test_the_account_center_has_a_card_linking_to_the_page(
        self, client, signed_in
    ) -> None:
        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        cards = page.split(CARDS_ID, 1)[1]
        assert FOLLOWING_URL in links_in(cards)

    def test_a_project_without_the_activity_urls_gets_no_card(
        self, client, signed_in
    ) -> None:
        urls = types.ModuleType("urls_without_activity")
        urls.urlpatterns = [
            route
            for route in project_urls.urlpatterns
            if getattr(route, "urlconf_name", None) is not activity_urls
        ]

        with override_settings(ROOT_URLCONF=urls):
            page = client.get(ACCOUNT_CENTER_URL).content.decode()

        assert "following" not in page.split(CARDS_ID, 1)[1]


class TestNoSidebarEntry:
    def test_the_extra_adds_nothing_to_the_sidebar(self) -> None:
        # A host project decides where a feed lives, so the package puts none
        # in the sidebar.
        with_extra, _ = menu_entries_with("actstream")
        without, _ = menu_entries_with()

        assert with_extra == without
