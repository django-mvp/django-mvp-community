"""Fixtures shared across the test suite."""

import os

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler
from generic_notifications import send_notification

from demo.notifications import NewFollower, ReplyReceived
from tests.factories import UserFactory


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
    def make(count, recipient=None, notification_type=NewFollower):
        return [
            send_notification(
                recipient=recipient or person,
                notification_type=notification_type,
                subject=f"Notification {index}",
            )
            for index in range(count)
        ]

    return make
