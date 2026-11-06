"""The unsubscribe address: what it names, how it is signed and what turning it off changes."""

import pytest
from django.contrib.sites.models import Site
from django.core import signing
from django.urls import reverse
from generic_notifications.models import NotificationTypeChannelPreference
from generic_notifications.registry import registry

from demo.notifications import CourseUpdated, NewFollower, ReplyReceived, SecurityNotice
from mvp_community.integrations.notifications.unsubscribe import UnsubscribeLink

KEYS = [ReplyReceived.key, NewFollower.key]


def email_preference(person, notification_type):
    return NotificationTypeChannelPreference.objects.filter(
        user=person, notification_type=notification_type.key, channel="email"
    ).first()


class TestForEmail:
    def test_it_names_the_person_and_the_types(self, person) -> None:
        link = UnsubscribeLink.for_email(person, KEYS)

        assert link.user == person
        assert sorted(link.type_keys) == sorted(KEYS)

    def test_an_always_sent_type_is_left_out(self, person) -> None:
        link = UnsubscribeLink.for_email(person, [*KEYS, SecurityNotice.key])

        assert SecurityNotice.key not in link.type_keys
        assert sorted(link.type_keys) == sorted(KEYS)

    def test_it_is_none_when_nothing_is_left(self, person) -> None:
        assert UnsubscribeLink.for_email(person, [SecurityNotice.key]) is None

    def test_a_type_no_longer_registered_is_left_out(self, person) -> None:
        link = UnsubscribeLink.for_email(person, [*KEYS, "removed_type"])

        assert sorted(link.type_keys) == sorted(KEYS)


class TestAddress:
    def test_the_path_leads_to_the_unsubscribe_page(self, person) -> None:
        link = UnsubscribeLink.for_email(person, KEYS)

        token = link.path.rstrip("/").rsplit("/", 1)[-1]

        assert link.path == reverse(
            "mvp_community_notifications:unsubscribe", args=[token]
        )

    def test_the_url_is_the_path_on_the_sites_address(self, person, db) -> None:
        Site.objects.filter(pk=1).update(domain="example.org")
        link = UnsubscribeLink.for_email(person, KEYS)

        assert link.url().endswith(f"//example.org{link.path}")


class TestRead:
    def test_it_reads_back_the_person_and_the_types(self, person) -> None:
        link = UnsubscribeLink.for_email(person, KEYS)
        token = link.path.rstrip("/").rsplit("/", 1)[-1]

        read = UnsubscribeLink.read(token)

        assert read.user == person
        assert sorted(t.key for t in read.types) == sorted(KEYS)

    def test_an_altered_token_is_invalid(self, person) -> None:
        link = UnsubscribeLink.for_email(person, KEYS)
        token = link.path.rstrip("/").rsplit("/", 1)[-1]

        assert UnsubscribeLink.read(token[:-2] + "xx") is None

    def test_a_token_that_is_not_a_token_is_invalid(self, db) -> None:
        assert UnsubscribeLink.read("nonsense") is None

    def test_a_person_who_no_longer_exists_is_invalid(self, person) -> None:
        link = UnsubscribeLink.for_email(person, KEYS)
        token = link.path.rstrip("/").rsplit("/", 1)[-1]
        person.delete()

        assert UnsubscribeLink.read(token) is None

    def test_types_that_are_not_registered_are_invalid(self, person) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": ["gone"]},
            salt="mvp_community.notifications.unsubscribe",
        )

        assert UnsubscribeLink.read(token) is None

    def test_an_unregistered_type_is_dropped_from_one_that_is_registered(
        self, person
    ) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": ["gone", ReplyReceived.key]},
            salt="mvp_community.notifications.unsubscribe",
        )

        assert [t.key for t in UnsubscribeLink.read(token).types] == [ReplyReceived.key]

    def test_a_type_since_made_always_sent_is_dropped(self, person) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": [ReplyReceived.key, SecurityNotice.key]},
            salt="mvp_community.notifications.unsubscribe",
        )

        assert [t.key for t in UnsubscribeLink.read(token).types] == [ReplyReceived.key]

    def test_a_link_to_only_an_always_sent_type_is_invalid(self, person) -> None:
        token = signing.dumps(
            {"u": person.pk, "t": [SecurityNotice.key]},
            salt="mvp_community.notifications.unsubscribe",
        )

        assert UnsubscribeLink.read(token) is None


class TestEmailedAndTurnOff:
    @pytest.fixture
    def link(self, person):
        return UnsubscribeLink.for_email(person, KEYS)

    def test_both_types_reach_the_person_by_email_to_begin_with(self, link) -> None:
        assert sorted(t.key for t in link.emailed()) == sorted(KEYS)

    def test_turning_off_returns_the_types_it_changed(self, link) -> None:
        changed = link.turn_off()

        assert sorted(t.key for t in changed) == sorted(KEYS)
        assert link.emailed() == []

    def test_turning_off_a_second_time_changes_nothing(self, link) -> None:
        link.turn_off()

        assert link.turn_off() == []

    def test_it_leaves_other_types_and_the_site_channel_alone(
        self, person, link
    ) -> None:
        link.turn_off()

        assert email_preference(person, CourseUpdated) is None
        assert not NotificationTypeChannelPreference.objects.filter(
            user=person, channel="website"
        ).exists()

    def test_a_type_already_off_is_not_reported(self, person) -> None:
        ReplyReceived.disable_channel(person, registry.get_channel("email"))
        link = UnsubscribeLink.for_email(person, KEYS)

        assert [t.key for t in link.turn_off()] == [NewFollower.key]
