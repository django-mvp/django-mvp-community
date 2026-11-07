"""The notifications extra's set-up and its system check."""

import pytest
from django.core.checks import Error
from generic_notifications.channels import EmailChannel as LibraryEmailChannel
from generic_notifications.registry import registry
from generic_notifications.types import NotificationType, SystemMessage

from mvp_community.integrations.notifications.channels import NotificationEmailChannel
from mvp_community.integrations.notifications.checks import check_email_channel_named
from mvp_community.integrations.notifications.frequencies import WeeklyFrequency
from mvp_community.integrations.notifications.setup import configure


@pytest.fixture
def restore_registry():
    """Put the registry back as the app's start-up left it."""
    saved = (
        dict(registry._type_classes),
        dict(registry._channel_classes),
        dict(registry._frequency_classes),
        set(registry._registered_class_ids),
    )
    yield
    (
        registry._type_classes,
        registry._channel_classes,
        registry._frequency_classes,
        registry._registered_class_ids,
    ) = saved


class TestConfigure:
    def test_start_up_registers_the_packages_email_channel(self) -> None:
        # The demo installs the mail extra, and nothing here has called configure.
        assert registry.get_channel("email") is NotificationEmailChannel

    def test_with_the_mail_extra_the_packages_channel_replaces_the_librarys(
        self, restore_registry
    ) -> None:
        registry.register_channel(LibraryEmailChannel, force=True)

        configure(mail_installed=True)

        assert registry.get_channel("email") is NotificationEmailChannel

    def test_without_the_mail_extra_no_email_channel_is_registered(
        self, restore_registry
    ) -> None:
        configure(mail_installed=False)

        assert "email" not in [channel.key for channel in registry.get_all_channels()]

    @pytest.mark.parametrize("order", [(True, False), (False, True)])
    def test_calling_it_twice_leaves_the_registry_the_last_call_describes(
        self, restore_registry, order
    ) -> None:
        for mail_installed in order:
            configure(mail_installed=mail_installed)
        once = (
            list(registry._channel_classes.items()),
            list(registry._frequency_classes.items()),
            list(registry._type_classes.items()),
        )

        configure(mail_installed=order[-1])

        assert (
            list(registry._channel_classes.items()),
            list(registry._frequency_classes.items()),
            list(registry._type_classes.items()),
        ) == once
        assert ("email" in registry._channel_classes) is order[-1]

    def test_the_weekly_digest_is_a_registered_frequency(self) -> None:
        assert registry.get_frequency("weekly") is WeeklyFrequency

    def test_the_librarys_system_message_is_removed(self, restore_registry) -> None:
        registry.register_type(SystemMessage, force=True)

        configure(mail_installed=True)

        assert SystemMessage.key not in [t.key for t in registry.get_all_types()]


class TestCheckEmailChannelNamed:
    @pytest.fixture
    def named(self, restore_registry):
        """Register a type that names the given channel, and return the check's errors."""

        def register(channel):
            class Named(NotificationType):
                key = "named_the_channel"
                name = "Named"
                description = "A type that names a channel"
                required_channels = [channel]

            registry.register_type(Named, force=True)
            return check_email_channel_named(app_configs=None)

        return register

    def test_a_type_naming_the_librarys_channel_is_reported(self, named) -> None:
        errors = named(LibraryEmailChannel)

        assert [error.id for error in errors] == ["mvp_community.E001"]
        assert all(isinstance(error, Error) for error in errors)

    def test_a_default_channel_naming_the_librarys_channel_is_reported(
        self, restore_registry
    ) -> None:
        class Named(NotificationType):
            key = "named_as_default"
            name = "Named"
            description = "A type that names a channel by default"
            default_channels = [LibraryEmailChannel]

        registry.register_type(Named, force=True)

        errors = check_email_channel_named(app_configs=None)

        assert [error.id for error in errors] == ["mvp_community.E001"]

    def test_a_type_naming_the_packages_channel_is_not_reported(self, named) -> None:
        assert named(NotificationEmailChannel) == []

    def test_the_demos_types_are_not_reported(self) -> None:
        assert check_email_channel_named(app_configs=None) == []

    def test_nothing_is_reported_when_the_librarys_channel_is_the_registered_one(
        self, named, restore_registry
    ) -> None:
        registry.register_channel(LibraryEmailChannel, force=True)

        assert named(LibraryEmailChannel) == []
