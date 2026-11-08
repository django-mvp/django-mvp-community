"""The preferences page, with and without the push channel."""

from datetime import timedelta

import pytest
from django.urls import include, path, reverse
from django.utils import timezone
from generic_notifications.registry import registry
from push_notifications.models import WebPushDevice

from mvp_community.integrations.push.subscriptions import card_context
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

        assert set(context) == {"subscriptions", "worker_url", "subscribe_url"}
