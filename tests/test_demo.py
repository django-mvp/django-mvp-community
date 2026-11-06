"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

import pytest
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.shortcuts import resolve_url
from django.test import override_settings
from django.urls import reverse
from django.utils import translation
from post_office import mail as post_office_mail
from post_office.models import STATUS, Email, EmailTemplate

import demo.settings as demo_settings

# The address a page guarded by LoginRequiredMixin sends an anonymous visitor to.
SIGN_IN_URL = resolve_url(settings.LOGIN_URL)


class TestSignIn:
    def test_the_sign_in_page_renders(self, client, db) -> None:
        assert client.get(SIGN_IN_URL).status_code == 200

    def test_a_seeded_account_can_sign_in(self, client, django_user_model) -> None:
        django_user_model.objects.create_user(
            username="regular.user@example.com", password="password"
        )
        response = client.post(
            SIGN_IN_URL,
            {"username": "regular.user@example.com", "password": "password"},
        )
        assert response.status_code == 302
        assert "_auth_user_id" in client.session


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        # A template that fails to extend the shell still returns 200.
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_links_the_pages_that_exist(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("overview")}"' in sidebar


@pytest.mark.django_db
class TestOverviewPageInABrowser:
    # Only what a real browser can measure belongs here. A check that works on
    # rendered HTML goes in the class above, which cannot skip.

    def test_the_page_loads_without_a_console_error(
        self, chromium, live_server, page
    ) -> None:
        # A script that throws leaves the markup intact and the page broken.
        errors: list[str] = []
        page.on("pageerror", lambda exception: errors.append(str(exception)))

        page.goto(live_server.url + reverse("overview"))

        assert errors == []


class TestDemoNotificationTypes:
    # The demo registers its types from DemoConfig.ready(), so a page that lists
    # them has something to list.

    @pytest.mark.parametrize(
        "key", ["reply_received", "new_follower", "course_updated", "security_notice"]
    )
    def test_the_demo_registers_its_notification_types(self, key: str) -> None:
        from generic_notifications.registry import registry

        assert registry.get_type(key).key == key

    def test_a_security_notice_is_always_sent_on_the_site(self) -> None:
        from generic_notifications.channels import WebsiteChannel
        from generic_notifications.registry import registry

        assert WebsiteChannel in registry.get_type("security_notice").required_channels


class TestBellInTheShell:
    BELL = 'id="mvp-community-bell"'

    def test_the_count_is_shown_to_a_person_with_unread_notifications(
        self, client, signed_in, make_notifications
    ) -> None:
        make_notifications(3)

        page = client.get(reverse("overview")).content.decode()

        assert '<span aria-hidden="true">3</span>' in page

    def test_no_count_is_shown_when_nothing_is_unread(self, client, signed_in) -> None:
        page = client.get(reverse("overview")).content.decode()

        assert self.BELL in page
        assert 'class="badge' not in page.split(self.BELL, 1)[1].split("</div>", 1)[0]

    def test_the_bell_links_to_the_notifications_page(self, client, signed_in) -> None:
        page = client.get(reverse("overview")).content.decode()

        bell = page.split(self.BELL, 1)[1].split("</div>", 1)[0]
        assert f'href="{reverse("mvp_community_notifications:list")}"' in bell

    def test_the_bell_refreshes_itself_from_its_route_and_on_the_changed_event(
        self, client, signed_in
    ) -> None:
        page = client.get(reverse("overview")).content.decode()

        bell = page.split(self.BELL, 1)[1].split(">", 1)[0]
        assert f'hx-get="{reverse("mvp_community_notifications:bell")}"' in bell
        assert "notifications:changed" in bell
        assert "every 60s" in bell

    def test_a_signed_out_visitor_sees_no_bell(self, client, db) -> None:
        assert self.BELL not in client.get(reverse("overview")).content.decode()


class TestSendNotificationView:
    URL = "/send-notification/"

    def test_it_sends_the_signed_in_person_a_notification_and_asks_the_bell_to_refresh(
        self, client, signed_in
    ) -> None:
        response = client.post(self.URL)

        assert response.status_code == 204
        assert response["HX-Trigger"] == "notifications:changed"
        assert signed_in.notifications.count() == 1

    def test_signed_out_is_sent_to_sign_in(self, client, db) -> None:
        response = client.post(self.URL)

        assert response.status_code == 302
        assert response["Location"].startswith(SIGN_IN_URL)


class TestMail:
    # The settings are the demo's own, so deleting a line of the documented
    # configuration fails these. Only the backend the queue hands email to is
    # replaced: django-anymail's test backend, which keeps the suite on the
    # path a provider takes.

    @pytest.fixture
    def configure(self, db):
        def apply(priority: str):
            return override_settings(
                EMAIL_BACKEND=demo_settings.EMAIL_BACKEND,
                POST_OFFICE={
                    **demo_settings.POST_OFFICE,
                    "BACKENDS": {"default": "anymail.backends.test.EmailBackend"},
                    "DEFAULT_PRIORITY": priority,
                },
            )

        return apply

    def send(self) -> None:
        mail.send_mail("Hello", "Body", "from@example.com", ["to@example.com"])

    def test_an_email_is_queued_and_not_handed_to_the_backend(self, configure) -> None:
        with configure("medium"):
            self.send()

        email = Email.objects.get()
        assert email.status == STATUS.queued
        assert mail.outbox == []

    def test_sending_the_queue_hands_it_over_and_logs_it_as_sent(
        self, configure
    ) -> None:
        with configure("medium"):
            self.send()
            call_command("send_queued_mail")

        email = Email.objects.get()
        assert email.status == STATUS.sent
        assert email.logs.get().status == STATUS.sent
        assert [message.to for message in mail.outbox] == [["to@example.com"]]

    def test_with_a_priority_of_now_it_is_handed_over_during_the_call(
        self, configure
    ) -> None:
        with configure("now"):
            self.send()

        assert [message.to for message in mail.outbox] == [["to@example.com"]]
        email = Email.objects.get()
        assert email.status == STATUS.sent
        assert email.logs.count() == 1


class TestStoredTemplate:
    # A template staff write in the admin, extending the layout django-mvp
    # ships. The German translation writes its own footer because the layout's
    # default one is English.
    SENT_BY = "Sent by"

    @pytest.fixture
    def welcome(self, db) -> EmailTemplate:
        layout = '{% extends "mvp/email/base.html" %}'
        english = EmailTemplate.objects.create(
            name="welcome",
            subject="Welcome",
            html_content=layout
            + "{% block body %}<h1>Hello there</h1><p>English body.</p>{% endblock %}",
        )
        EmailTemplate.objects.create(
            name="welcome",
            language="de",
            default_template=english,
            subject="Willkommen",
            html_content=layout
            + "{% block body %}<h1>Hallo zusammen</h1><p>Deutscher Text.</p>{% endblock %}"
            + "{% block footer %}<p>Deutsche Fusszeile.</p>{% endblock %}",
        )
        return english

    def test_a_translation_is_sent_in_the_layout_with_its_own_footer(
        self, welcome
    ) -> None:
        with translation.override("de"):
            email = post_office_mail.send(
                "to@example.com",
                "from@example.com",
                template="welcome",
                language="de",
                priority="medium",
            )

        assert email.subject == "Willkommen"
        html = email.html_message
        assert "Deutscher Text." in html
        assert "English body." not in html
        assert "Deutsche Fusszeile." in html
        assert self.SENT_BY not in html
        assert '<html lang="de"' in html
        # Inlined: the rule from the layout's style element is on the element.
        assert "<h1 style=" in html

    def test_a_language_with_no_translation_raises_and_writes_no_row(
        self, welcome
    ) -> None:
        with pytest.raises(EmailTemplate.DoesNotExist):
            post_office_mail.send(
                "to@example.com",
                "from@example.com",
                template="welcome",
                language="fr",
                priority="medium",
            )

        assert not Email.objects.exists()

    def test_an_edit_to_a_translation_reaches_the_next_email(self, welcome) -> None:
        # django-post-office clears a different cache entry from the one it
        # reads when a translation is saved, so with its template cache on
        # this edit would be ignored. The demo turns the cache off.
        def send_in_german() -> Email:
            with translation.override("de"):
                return post_office_mail.send(
                    "to@example.com",
                    "from@example.com",
                    template="welcome",
                    language="de",
                    priority="medium",
                )

        send_in_german()
        german = EmailTemplate.objects.get(name="welcome", language="de")
        german.subject = "Herzlich willkommen"
        german.save()

        assert send_in_german().subject == "Herzlich willkommen"
