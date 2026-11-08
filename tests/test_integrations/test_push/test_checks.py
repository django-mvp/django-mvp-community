"""The system check that guards the push settings."""

import pytest
from push_notifications.settings import PUSH_NOTIFICATIONS_SETTINGS

from mvp_community.integrations.push.checks import check_push_settings

CLAIMS = {"sub": "mailto:admin@example.com"}


def ids(errors) -> list[str]:
    return [error.id for error in errors]


class TestCheckPushSettings:
    def test_the_demos_settings_raise_nothing(self) -> None:
        assert check_push_settings(app_configs=None) == []

    def test_a_private_key_that_is_none_is_reported(self, monkeypatch) -> None:
        # The library fills both keys with None when it loads, so None is the
        # value a project that never set them has.
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_PRIVATE_KEY", None)

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002"]
        assert "WP_PRIVATE_KEY" in errors[0].msg

    def test_a_private_key_that_is_absent_is_reported(self, monkeypatch) -> None:
        monkeypatch.delitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_PRIVATE_KEY")

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002"]
        assert "WP_PRIVATE_KEY" in errors[0].msg

    @pytest.mark.parametrize("claims", [None, {}])
    def test_empty_claims_are_reported(self, monkeypatch, claims) -> None:
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_CLAIMS", claims)

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002"]
        assert "WP_CLAIMS" in errors[0].msg

    def test_claims_that_are_absent_are_reported(self, monkeypatch) -> None:
        monkeypatch.delitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_CLAIMS")

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002"]

    def test_claims_with_no_sub_are_reported(self, monkeypatch) -> None:
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_CLAIMS", {"aud": "x"})

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002"]
        assert "WP_CLAIMS" in errors[0].msg

    def test_each_missing_setting_is_its_own_error(self, monkeypatch) -> None:
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_PRIVATE_KEY", None)
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_CLAIMS", None)

        errors = check_push_settings(app_configs=None)

        assert ids(errors) == ["mvp_community.E002", "mvp_community.E002"]

    def test_nothing_is_reported_when_both_are_set(self, monkeypatch) -> None:
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_PRIVATE_KEY", "a-key")
        monkeypatch.setitem(PUSH_NOTIFICATIONS_SETTINGS, "WP_CLAIMS", CLAIMS)

        assert check_push_settings(app_configs=None) == []
