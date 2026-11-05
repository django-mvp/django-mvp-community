"""The unread-count tag, rendered as a template uses it."""

from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import RequestFactory
from generic_notifications import send_notification
from generic_notifications.channels import EmailChannel, WebsiteChannel

from demo.notifications import ReplyReceived

SOURCE = "{% load mvp_community_notifications %}{% notifications_unread_count as count %}[{{ count }}]"


def render_for(user) -> str:
    request = RequestFactory().get("/")
    request.user = user
    return Template(SOURCE).render(Context({"request": request}))


class TestNotificationsUnreadCount:
    def test_it_counts_the_persons_unread_site_notifications(
        self, person, make_notifications
    ) -> None:
        read, *_unread = make_notifications(3)
        read.mark_as_read()

        assert render_for(person) == "[2]"

    def test_it_counts_nothing_for_a_person_with_none(self, person) -> None:
        assert render_for(person) == "[0]"

    def test_it_gives_nothing_to_a_signed_out_visitor(self, db) -> None:
        assert render_for(AnonymousUser()) == "[None]"

    def test_it_gives_nothing_without_a_request(self, db) -> None:
        assert Template(SOURCE).render(Context({})) == "[None]"

    def test_a_notification_only_on_another_channel_is_not_counted(
        self, person
    ) -> None:
        ReplyReceived.enable_channel(person, EmailChannel)
        ReplyReceived.disable_channel(person, WebsiteChannel)
        send_notification(
            recipient=person, notification_type=ReplyReceived, subject="By email"
        )

        assert render_for(person) == "[0]"
