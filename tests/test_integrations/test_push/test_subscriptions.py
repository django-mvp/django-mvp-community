"""The preferences page, with and without the push channel."""

from base64 import urlsafe_b64decode
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import include, path, reverse
from django.utils import timezone
from generic_notifications.registry import registry
from push_notifications.models import WebPushDevice
from py_vapid import Vapid01
from py_vapid.utils import b64urlencode

from mvp_community.integrations.push.subscriptions import (
    Browser,
    application_server_key,
    card_context,
    is_push_endpoint,
)
from tests.urls import urlpatterns as suite_urlpatterns

PREFERENCES_URL = reverse("mvp_community_notifications:preferences")


def route(request):
    """Stand in for a push view, which later tasks add."""
    raise NotImplementedError


push_urlpatterns = (
    [
        path("worker.js", route, name="worker"),
        path("subscribe/", route, name="subscribe"),
        path("<int:pk>/stop/", route, name="stop"),
    ],
    "mvp_community_push",
)

urlpatterns = [
    *suite_urlpatterns,
    path("notifications/push/", include(push_urlpatterns)),
]


@pytest.fixture
def with_push_urls(settings):
    """Serve the routes the push views will own, as stand-ins."""
    settings.ROOT_URLCONF = __name__


def subscribe(user, endpoint, **fields):
    """Store a push subscription for ``user``."""
    return WebPushDevice.objects.create(
        user=user,
        registration_id=endpoint,
        p256dh="p256dh-key",
        auth="auth-secret",
        browser="CHROME",
        **fields,
    )


@pytest.fixture
def without_push(monkeypatch):
    channels = {
        key: channel
        for key, channel in registry._channel_classes.items()
        if key != "push"
    }
    monkeypatch.setattr(registry, "_channel_classes", channels)


class TestPreferencesWithoutPush:
    def test_the_page_has_no_push_card(self, client, signed_in, without_push) -> None:
        response = client.get(PREFERENCES_URL)

        assert response.status_code == 200
        assert "push" not in response.context

    def test_the_page_has_no_push_column(self, client, signed_in, without_push) -> None:
        context = client.get(PREFERENCES_URL).context

        assert "push" not in [channel.key for channel in context["channels"]]
        assert all("push" not in row["channels"] for row in context["preferences"])


@pytest.mark.usefixtures("with_push_urls")
class TestPreferencesWithPush:
    def test_the_page_has_a_push_card_and_a_push_column(
        self, client, signed_in
    ) -> None:
        context = client.get(PREFERENCES_URL).context

        assert "push" in context
        assert "push" in [channel.key for channel in context["channels"]]

    def test_the_card_has_the_two_urls(self, client, signed_in) -> None:
        push = client.get(PREFERENCES_URL).context["push"]

        assert str(push["worker_url"]) == reverse("mvp_community_push:worker")
        assert str(push["subscribe_url"]) == reverse("mvp_community_push:subscribe")

    def test_the_card_carries_the_key_and_the_two_urls_as_data_attributes(
        self, client, signed_in
    ) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        assert f'data-application-server-key="{application_server_key()}"' in page
        assert f'data-worker-url="{reverse("mvp_community_push:worker")}"' in page
        assert f'data-subscribe-url="{reverse("mvp_community_push:subscribe")}"' in page

    def test_the_card_lists_active_subscriptions_newest_first(
        self, client, signed_in
    ) -> None:
        older = subscribe(signed_in, "https://fcm.googleapis.com/older")
        newer = subscribe(signed_in, "https://fcm.googleapis.com/newer")
        WebPushDevice.objects.filter(pk=older.pk).update(
            date_created=timezone.now() - timedelta(days=1)
        )

        push = client.get(PREFERENCES_URL).context["push"]

        assert [row.pk for row in push["subscriptions"]] == [newer.pk, older.pk]

    def test_the_card_leaves_out_inactive_and_other_peoples_subscriptions(
        self, client, signed_in, django_user_model
    ) -> None:
        mine = subscribe(signed_in, "https://fcm.googleapis.com/mine")
        subscribe(signed_in, "https://fcm.googleapis.com/off", active=False)
        stranger = django_user_model.objects.create_user("stranger")
        subscribe(stranger, "https://fcm.googleapis.com/theirs")

        push = client.get(PREFERENCES_URL).context["push"]

        assert [row.pk for row in push["subscriptions"]] == [mine.pk]

    def test_each_row_stops_at_its_own_url(self, client, signed_in) -> None:
        device = subscribe(signed_in, "https://fcm.googleapis.com/mine")

        page = client.get(PREFERENCES_URL).content.decode()

        assert reverse("mvp_community_push:stop", args=[device.pk]) in page

    def test_no_row_when_there_are_no_subscriptions(self, client, signed_in) -> None:
        page = client.get(PREFERENCES_URL).content.decode()

        assert "/stop/" not in page


class TestCardContext:
    def test_it_carries_the_subscriptions_and_the_two_urls_only(
        self, rf, person, with_push_urls
    ) -> None:
        request = rf.get(PREFERENCES_URL)
        request.user = person

        context = card_context(request)

        assert set(context) == {
            "subscriptions",
            "worker_url",
            "subscribe_url",
            "application_server_key",
        }
        assert context["application_server_key"] == application_server_key()


IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
IPAD = (
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
ANDROID = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)
WINDOWS_FIREFOX = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
)


class TestBrowser:
    def test_an_iphone_is_a_phone_named_by_its_device(self) -> None:
        browser = Browser.from_user_agent(IPHONE)

        assert browser.family == "Safari"
        assert browser.place == "iPhone"
        assert browser.kind == "phone"

    def test_an_android_browser_is_a_phone_named_by_its_system(self) -> None:
        browser = Browser.from_user_agent(ANDROID)

        assert browser.family == "Chrome"
        assert browser.place == "Android"
        assert browser.kind == "phone"

    def test_an_ipad_is_a_tablet(self) -> None:
        browser = Browser.from_user_agent(IPAD)

        assert browser.place == "iPad"
        assert browser.kind == "tablet"

    def test_a_desktop_browser_is_a_computer_named_by_its_system(self) -> None:
        browser = Browser.from_user_agent(WINDOWS_FIREFOX)

        assert browser.family == "Firefox"
        assert browser.place == "Windows"
        assert browser.kind == "computer"

    def test_an_empty_user_agent_has_a_fallback_label(self) -> None:
        browser = Browser.from_user_agent("")

        assert browser.family == ""
        assert browser.kind == "computer"
        assert str(browser.label)

    def test_the_label_names_the_family_and_the_place(self) -> None:
        label = str(Browser.from_user_agent(WINDOWS_FIREFOX).label)

        assert "Firefox" in label
        assert "Windows" in label


class TestApplicationServerKey:
    def decode(self, key):
        return urlsafe_b64decode(key + "=" * (-len(key) % 4))

    def make_key(self):
        vapid = Vapid01()
        vapid.generate_keys()
        return vapid

    def test_a_key_string_gives_the_65_byte_public_key(self) -> None:
        vapid = self.make_key()
        settings_dict = {
            "WP_PRIVATE_KEY": b64urlencode(
                vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
            )
        }

        with patch.dict(
            "push_notifications.settings.PUSH_NOTIFICATIONS_SETTINGS", settings_dict
        ):
            key = application_server_key()

        assert len(self.decode(key)) == 65

    def test_a_key_file_gives_the_65_byte_public_key(self, tmp_path) -> None:
        vapid = self.make_key()
        path = tmp_path / "private_key.pem"
        vapid.save_key(str(path))

        with patch.dict(
            "push_notifications.settings.PUSH_NOTIFICATIONS_SETTINGS",
            {"WP_PRIVATE_KEY": str(path)},
        ):
            key = application_server_key()

        assert len(self.decode(key)) == 65

    def test_two_keys_give_two_results(self, tmp_path) -> None:
        keys = []
        for name in ("one.pem", "two.pem"):
            path = tmp_path / name
            self.make_key().save_key(str(path))
            with patch.dict(
                "push_notifications.settings.PUSH_NOTIFICATIONS_SETTINGS",
                {"WP_PRIVATE_KEY": str(path)},
            ):
                keys.append(application_server_key())

        assert keys[0] != keys[1]


class TestPushEndpoint:
    @pytest.mark.parametrize(
        "url",
        [
            "https://fcm.googleapis.com/fcm/send/abc",
            "https://updates.push.services.mozilla.com/wpush/v2/abc",
            "https://web.push.apple.com/abc",
            "https://wns2-par02p.notify.windows.com/w/?token=abc",
            "https://api.push.apple.com/3/device/abc",
        ],
    )
    def test_a_major_push_service_is_accepted(self, url) -> None:
        assert is_push_endpoint(url)

    @pytest.mark.parametrize(
        "url",
        [
            "http://fcm.googleapis.com/fcm/send/abc",
            "https://example.org/push",
            "https://fcm.googleapis.com.example.org/abc",
            "https://example.org/?next=fcm.googleapis.com",
            "https://user@fcm.googleapis.com@example.org/abc",
            "notaurl",
            "",
        ],
    )
    def test_anything_else_is_refused(self, url) -> None:
        assert not is_push_endpoint(url)
