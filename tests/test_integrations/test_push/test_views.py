"""The push views, asserted through what they store and answer."""

import copy
import json
from pathlib import Path

import pytest
import requests
from django.contrib.messages import get_messages
from django.urls import reverse
from generic_notifications.registry import registry
from push_notifications.models import WebPushDevice

from mvp_community.integrations.push.channels import PushChannel
from mvp_community.integrations.push.views import SUBSCRIPTION_LIMIT
from tests.factories import AUTH, P256DH, PushSubscriptionFactory, urlsafe

SUBSCRIBE_URL = "/notifications/push/subscribe/"
OVERRIDES = Path(__file__).resolve().parent.parent.parent / "templates" / "overrides"
ENDPOINT = "https://fcm.googleapis.com/fcm/send/abc"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0"


@pytest.fixture
def sent(monkeypatch):
    """Record each payload sent, keyed by the subscription's endpoint."""
    sends = []

    def record(self, message, **kwargs):
        sends.append((self.registration_id, message))

    monkeypatch.setattr(WebPushDevice, "send_message", record)
    return sends


def body(endpoint=ENDPOINT, previous=None, **keys):
    keys = {"p256dh": P256DH, "auth": AUTH} | keys
    data = {"endpoint": endpoint, "keys": keys}
    if previous is not None:
        data["previous"] = previous
    return json.dumps(data)


def post(client, data, user_agent=USER_AGENT):
    return client.post(
        reverse("mvp_community_push:subscribe"),
        data,
        content_type="application/json",
        HTTP_USER_AGENT=user_agent,
    )


class TestSubscribeView:
    def test_the_route_is_where_the_card_expects_it(self) -> None:
        assert reverse("mvp_community_push:subscribe") == SUBSCRIBE_URL

    def test_a_signed_out_post_is_refused_and_stores_nothing(
        self, client, sent, db
    ) -> None:
        response = post(client, body())

        assert response.status_code in (302, 403)
        assert not WebPushDevice.objects.exists()
        assert sent == []

    def test_a_valid_post_stores_one_active_subscription_and_sends_a_test(
        self, client, signed_in, sent
    ) -> None:
        response = post(client, body())

        assert response.status_code == 204
        subscription = WebPushDevice.objects.get()
        assert subscription.user == signed_in
        assert subscription.registration_id == ENDPOINT
        assert subscription.p256dh == P256DH
        assert subscription.auth == AUTH
        assert subscription.active
        assert subscription.name == USER_AGENT
        assert [endpoint for endpoint, _ in sent] == [ENDPOINT]

    def test_the_test_push_opens_the_preferences_page(
        self, client, signed_in, sent
    ) -> None:
        post(client, body())

        payload = json.loads(sent[0][1])
        assert payload["url"] == reverse("mvp_community_notifications:preferences")
        assert payload["title"]
        assert payload["body"]

    def test_the_same_endpoint_twice_leaves_one_subscription(
        self, client, signed_in, sent
    ) -> None:
        post(client, body())
        WebPushDevice.objects.update(active=False)
        new_auth = urlsafe(bytes(range(16, 32)))
        post(client, body(auth=new_auth))

        subscription = WebPushDevice.objects.get()
        assert subscription.auth == new_auth
        assert subscription.active

    def test_the_same_endpoint_from_another_person_is_a_second_row(
        self, client, signed_in, sent, django_user_model
    ) -> None:
        post(client, body())
        client.force_login(django_user_model.objects.create_user("other"))
        post(client, body())

        assert WebPushDevice.objects.count() == 2

    def test_the_user_agent_is_cut_to_the_name_field(
        self, client, signed_in, sent
    ) -> None:
        response = post(client, body(), user_agent="x" * 400)

        assert response.status_code == 204
        assert len(WebPushDevice.objects.get().name) == 255

    @pytest.mark.parametrize(
        "data",
        [
            "not json",
            "[]",
            json.dumps({"endpoint": ENDPOINT}),
            json.dumps({"endpoint": ENDPOINT, "keys": {"p256dh": "a"}}),
            json.dumps({"endpoint": ENDPOINT, "keys": {"auth": "a"}}),
            json.dumps({"endpoint": ENDPOINT, "keys": "a"}),
            json.dumps({"endpoint": 5, "keys": {"p256dh": "a", "auth": "b"}}),
            body(p256dh=urlsafe(bytes(64))),
            body(p256dh="not base64!"),
            body(auth=urlsafe(bytes(17))),
            body(auth="?"),
            body(previous=5),
            body(endpoint="https://example.org/push"),
            body(endpoint="http://fcm.googleapis.com/fcm/send/abc"),
        ],
    )
    def test_a_bad_post_is_a_400_and_stores_nothing(
        self, client, signed_in, sent, data
    ) -> None:
        response = post(client, data)

        assert response.status_code == 400
        assert not WebPushDevice.objects.exists()
        assert sent == []

    def test_a_test_push_that_times_out_still_stores_the_subscription(
        self, client, signed_in, monkeypatch
    ) -> None:
        def time_out(self, message, **kwargs):
            raise requests.Timeout

        monkeypatch.setattr(WebPushDevice, "send_message", time_out)

        response = post(client, body())

        assert response.status_code == 204
        assert WebPushDevice.objects.count() == 1

    def test_a_get_is_405(self, client, signed_in) -> None:
        assert client.get(SUBSCRIBE_URL).status_code == 405

    def test_the_session_remembers_that_push_was_just_turned_on(
        self, client, signed_in, sent
    ) -> None:
        post(client, body())

        assert client.session["mvp_community_push_turned_on"] is True


class TestWorkerView:
    def test_the_route_is_where_the_card_expects_it(self) -> None:
        assert reverse("mvp_community_push:worker") == "/notifications/push/worker.js"

    def test_it_is_served_signed_out_as_javascript(self, client, db) -> None:
        response = client.get(reverse("mvp_community_push:worker"))

        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/javascript")

    def test_the_browser_revalidates_it_every_time(self, client, db) -> None:
        response = client.get(reverse("mvp_community_push:worker"))

        assert response["Cache-Control"] == "no-cache"

    def test_a_project_replaces_it_with_its_own_template(
        self, client, db, settings
    ) -> None:
        templates = copy.deepcopy(settings.TEMPLATES)
        templates[0]["DIRS"] = [*templates[0]["DIRS"], OVERRIDES / "worker"]
        settings.TEMPLATES = templates

        response = client.get(reverse("mvp_community_push:worker"))

        assert response.content.decode().strip() == "// project worker"


class TestStopView:
    def stop(self, client, pk):
        return client.post(reverse("mvp_community_push:stop", args=[pk]))

    def subscription(self, user, endpoint=ENDPOINT, name=USER_AGENT):
        return PushSubscriptionFactory(user=user, registration_id=endpoint, name=name)

    def test_the_route_is_where_the_card_expects_it(self) -> None:
        assert (
            reverse("mvp_community_push:stop", args=[7])
            == "/notifications/push/7/stop/"
        )

    def test_it_deletes_the_persons_own_subscription_and_returns_to_preferences(
        self, client, signed_in
    ) -> None:
        subscription = self.subscription(signed_in)

        response = self.stop(client, subscription.pk)

        assert not WebPushDevice.objects.filter(pk=subscription.pk).exists()
        assert response.status_code == 302
        assert response.url == reverse("mvp_community_notifications:preferences")

    def test_the_message_names_the_browser_by_its_label(
        self, client, signed_in
    ) -> None:
        subscription = self.subscription(signed_in)

        response = self.stop(client, subscription.pk)

        (message,) = get_messages(response.wsgi_request)
        assert "Firefox on Linux" in str(message)

    def test_another_persons_subscription_is_a_404_and_is_kept(
        self, client, signed_in, django_user_model
    ) -> None:
        stranger = django_user_model.objects.create_user("stranger")
        theirs = self.subscription(stranger)

        response = self.stop(client, theirs.pk)

        assert response.status_code == 404
        assert WebPushDevice.objects.filter(pk=theirs.pk).exists()

    def test_signed_out_changes_nothing(self, client, db, person) -> None:
        subscription = self.subscription(person)

        response = self.stop(client, subscription.pk)

        assert response.status_code in (302, 403)
        assert WebPushDevice.objects.filter(pk=subscription.pk).exists()

    def test_a_get_is_refused_and_changes_nothing(self, client, signed_in) -> None:
        subscription = self.subscription(signed_in)

        response = client.get(
            reverse("mvp_community_push:stop", args=[subscription.pk])
        )

        assert response.status_code == 405
        assert WebPushDevice.objects.filter(pk=subscription.pk).exists()


class TestSubscribeViewReplacingAnOldSubscription:
    # A browser whose subscription was made with an earlier key drops it and
    # sends its endpoint as ``previous``.
    OLD = "https://fcm.googleapis.com/fcm/send/old"

    def test_the_person_s_row_for_the_old_endpoint_is_deleted(
        self, client, signed_in, sent
    ) -> None:
        PushSubscriptionFactory(user=signed_in, registration_id=self.OLD)

        post(client, body(previous=self.OLD))

        endpoints = WebPushDevice.objects.values_list("registration_id", flat=True)
        assert list(endpoints) == [ENDPOINT]

    def test_another_person_s_row_for_it_is_kept(self, client, signed_in, sent) -> None:
        other = PushSubscriptionFactory(registration_id=self.OLD)

        post(client, body(previous=self.OLD))

        assert WebPushDevice.objects.filter(pk=other.pk).exists()


class TestSubscribeViewUsesTheRegisteredChannel:
    def test_a_project_s_push_channel_sends_the_test(
        self, client, signed_in, monkeypatch
    ) -> None:
        tested = []

        class ProjectPushChannel(PushChannel):
            def send_test(self, subscription):
                tested.append(subscription.registration_id)

        monkeypatch.setitem(registry._channel_classes, "push", ProjectPushChannel)

        post(client, body())

        assert tested == [ENDPOINT]


class TestSubscribeViewLimit:
    def test_the_person_s_oldest_beyond_the_limit_are_deleted(
        self, client, signed_in, sent
    ) -> None:
        kept = [
            PushSubscriptionFactory(user=signed_in) for _ in range(SUBSCRIPTION_LIMIT)
        ]

        post(client, body())

        endpoints = set(
            WebPushDevice.objects.filter(user=signed_in).values_list(
                "registration_id", flat=True
            )
        )
        assert len(endpoints) == SUBSCRIPTION_LIMIT
        assert ENDPOINT in endpoints
        assert kept[0].registration_id not in endpoints

    def test_another_person_s_subscriptions_are_not_counted(
        self, client, signed_in, sent
    ) -> None:
        PushSubscriptionFactory.create_batch(SUBSCRIPTION_LIMIT)

        post(client, body())

        assert WebPushDevice.objects.count() == SUBSCRIPTION_LIMIT + 1
