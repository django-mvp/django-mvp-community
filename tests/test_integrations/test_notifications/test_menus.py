"""The Account Center entry and card, asserted on the pages that draw them."""

import re

from django.urls import reverse

ACCOUNT_CENTER_URL = reverse("account-center")
PREFERENCES_URL = reverse("mvp_community_notifications:preferences")
CARDS_ID = 'id="account-center-cards"'


def links_in(markup: str) -> list[str]:
    return re.findall(r'<a[^>]*href="([^"]*)"', markup)


class TestAccountCenterEntry:
    def test_the_sidebar_links_to_the_preferences_page(self, client, signed_in) -> None:
        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        sidebar = page.split(CARDS_ID, 1)[0]
        assert PREFERENCES_URL in links_in(sidebar)

    def test_the_preferences_page_marks_its_own_entry_current(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        current = re.findall(r'<a[^>]*href="([^"]*)"[^>]*aria-current="page"', page)
        assert PREFERENCES_URL in current

    def test_the_preferences_page_keeps_the_account_center_in_the_sidebar(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        assert ACCOUNT_CENTER_URL in links_in(page)


class TestAccountCenterCard:
    def test_the_landing_page_has_a_card_linking_to_the_preferences_page(
        self, client, signed_in
    ) -> None:
        page = client.get(ACCOUNT_CENTER_URL).content.decode()

        cards = page.split(CARDS_ID, 1)[1]
        assert PREFERENCES_URL in links_in(cards)
