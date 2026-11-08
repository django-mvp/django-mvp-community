"""The push channel, asserted through the sends made to each subscription."""

import json
import logging

import pytest
import requests
from django.urls import reverse
from generic_notifications import send_notification
from generic_notifications.models import (
    NotificationFrequencyPreference,
    NotificationTypeChannelPreference,
)
from push_notifications.exceptions import WebPushError
from push_notifications.models import WebPushDevice

from demo.notifications import ReplyReceived
from mvp_community.integrations.push.channels import PushChannel
from tests.factories import PushSubscriptionFactory, UserFactory


def subscribe(user, endpoint, **fields):
    """Store a push subscription for ``user``."""
    return PushSubscriptionFactory(user=user, registration_id=endpoint, **fields)


@pytest.fixture
def sent(monkeypatch):
    """Record each payload sent, keyed by the subscription's endpoint."""
    sends = []

    def record(self, message, **kwargs):
        sends.append((self.registration_id, message))

    monkeypatch.setattr(WebPushDevice, "send_message", record)
    return sends


def notify(person, **fields):
    return send_notification(
        person,
        ReplyReceived,
        subject=fields.pop("subject", "Anna replied"),
        text=fields.pop("text", "Try the second exercise first."),
        **fields,
    )


class TestPushChannel:
    def test_it_sends_one_payload_to_each_active_subscription(
        self, person, sent
    ) -> None:
        subscribe(person, "https://push.example/one")
        subscribe(person, "https://push.example/two")

        notify(person)

        assert sorted(endpoint for endpoint, _ in sent) == [
            "https://push.example/one",
            "https://push.example/two",
        ]

    def test_an_inactive_subscription_gets_nothing(self, person, sent) -> None:
        subscribe(person, "https://push.example/off", active=False)
        subscribe(person, "https://push.example/on")

        notify(person)

        assert [endpoint for endpoint, _ in sent] == ["https://push.example/on"]

    def test_another_persons_subscription_gets_nothing(self, person, sent) -> None:
        subscribe(UserFactory(), "https://push.example/theirs")
        subscribe(person, "https://push.example/mine")

        notify(person)

        assert [endpoint for endpoint, _ in sent] == ["https://push.example/mine"]

    def test_the_payload_carries_the_title_body_and_the_open_view_path(
        self, person, sent
    ) -> None:
        subscribe(person, "https://push.example/one")

        notification = notify(person)

        payload = json.loads(sent[0][1])
        assert payload == {
            "title": "Anna replied",
            "body": "Try the second exercise first.",
            "url": reverse("mvp_community_notifications:open", args=[notification.pk]),
        }

    def test_a_long_body_is_cut(self, person, sent) -> None:
        subscribe(person, "https://push.example/one")

        notify(person, text="word " * 200)

        assert len(json.loads(sent[0][1])["body"]) <= 400

    def test_a_person_with_push_off_for_the_type_gets_nothing(
        self, person, sent
    ) -> None:
        subscribe(person, "https://push.example/one")
        NotificationTypeChannelPreference.objects.create(
            user=person,
            notification_type=ReplyReceived.key,
            channel=PushChannel.key,
            enabled=False,
        )

        notify(person)

        assert sent == []

    def test_a_type_set_to_a_daily_digest_is_still_pushed_at_once(
        self, person, sent
    ) -> None:
        subscribe(person, "https://push.example/one")
        NotificationFrequencyPreference.objects.create(
            user=person, notification_type=ReplyReceived.key, frequency="daily"
        )

        notify(person)

        assert len(sent) == 1

    @pytest.mark.parametrize(
        "error",
        [WebPushError("gone"), requests.Timeout("slow")],
        ids=["WebPushError", "Timeout"],
    )
    def test_a_failing_subscription_does_not_stop_the_next(
        self, person, monkeypatch, caplog, error
    ) -> None:
        subscribe(person, "https://push.example/bad")
        subscribe(person, "https://push.example/good")
        delivered = []

        def send(self, message, **kwargs):
            if self.registration_id.endswith("bad"):
                raise error
            delivered.append(self.registration_id)

        monkeypatch.setattr(WebPushDevice, "send_message", send)

        with caplog.at_level(logging.WARNING):
            notify(person)

        assert delivered == ["https://push.example/good"]
        assert [record.levelno for record in caplog.records] == [logging.WARNING]

    def test_the_payload_is_written_in_the_recipients_language(
        self, person, sent, monkeypatch
    ) -> None:
        from django.utils import translation
        from generic_notifications.models import Notification

        subscribe(person, "https://push.example/one")
        languages = []
        original = Notification.get_subject

        def get_subject(self):
            languages.append(translation.get_language())
            return original(self)

        monkeypatch.setattr(Notification, "get_subject", get_subject)
        monkeypatch.setattr(PushChannel, "recipient_language", lambda self, user: "fr")

        notify(person)

        assert languages == ["fr"]

    def test_the_recipients_language_is_the_sites(self, settings, person) -> None:
        settings.LANGUAGE_CODE = "de"

        assert PushChannel().recipient_language(person) == "de"
