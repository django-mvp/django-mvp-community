"""Fixtures shared across the test suite."""

import os
from datetime import timedelta

import pytest
from actstream import action as actstream_action
from actstream.actions import follow as actstream_follow
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django.utils import timezone
from django_cotton.compiler_regex import CottonCompiler
from generic_notifications import send_notification
from generic_notifications.models import Notification

from demo.notifications import NewFollower, ReplyReceived
from tests.factories import GroupFactory, UserFactory, UUIDUserFactory


@pytest.fixture(scope="session")
def render():
    # No request is involved, which holds components to rendering anywhere a
    # template does, including outside the request cycle.
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture(scope="session")
def chromium():
    # Locally a missing browser skips. In CI it fails, because a checks page
    # cannot tell a skipped test from a passing one.
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except (Error, ImportError) as exc:  # pragma: no cover - environment probe
        unavailable = f"no chromium available to measure the page with: {exc}"
        if os.environ.get("CI"):
            pytest.fail(
                f"{unavailable}\n\nThe tests workflow installs chromium through "
                "the shared workflow's `install-playwright` input. Reaching this "
                "means that input was dropped or its install step did not run.",
                pytrace=False,
            )
        pytest.skip(unavailable)


@pytest.fixture
def person(db):
    return UserFactory()


@pytest.fixture
def uuid_person(db, settings):
    # A host project may swap in a user model keyed by UUID rather than number.
    settings.AUTH_USER_MODEL = "uuid_users.UUIDUser"
    return UUIDUserFactory()


@pytest.fixture
def signed_in(client, person):
    client.force_login(person)
    return person


@pytest.fixture
def notification(person):
    return send_notification(
        recipient=person,
        notification_type=ReplyReceived,
        subject="Anna replied",
        text="Try the second exercise first.",
        url="/elsewhere/",
    )


@pytest.fixture
def make_notifications(person):
    # Each one arrived a minute before the last, so "newest first" has one answer.
    def make(count, recipient=None, notification_type=NewFollower):
        now = timezone.now()
        made = []
        for index in range(count):
            sent = send_notification(
                recipient=recipient or person,
                notification_type=notification_type,
                subject=f"Notification {index}",
            )
            Notification.objects.filter(pk=sent.pk).update(
                added=now - timedelta(minutes=index)
            )
            sent.refresh_from_db()
            made.append(sent)
        return made

    return make


@pytest.fixture
def group(db):
    return GroupFactory()


@pytest.fixture
def make_action():
    # Activity is recorded the way a host project records it, through
    # django-activity-stream. Each call is older than the last when minutes_ago
    # grows, so "newest first" has one answer.
    def make(actor, verb="finished", target=None, public=True, minutes_ago=0):
        from actstream.models import Action

        sent = actstream_action.send(actor, verb=verb, target=target, public=public)[0][
            1
        ]
        Action.objects.filter(pk=sent.pk).update(
            timestamp=timezone.now() - timedelta(minutes=minutes_ago)
        )
        sent.refresh_from_db()
        return sent

    return make


@pytest.fixture
def make_follow():
    # actor_only=False, as the follow control sends it: the person follows what
    # happens to the object as well as what it does. No "started following"
    # activity is recorded, so a test's feed holds only the activity it made.
    def make(follower, followed):
        return actstream_follow(follower, followed, actor_only=False, send_action=False)

    return make
