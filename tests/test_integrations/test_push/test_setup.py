"""The push extra's set-up."""

import pytest
from generic_notifications.registry import registry

from mvp_community.integrations.push.channels import PushChannel
from mvp_community.integrations.push.setup import configure


@pytest.fixture
def restore_registry():
    """Put the registry back as the app's start-up left it."""
    saved = (
        dict(registry._channel_classes),
        set(registry._registered_class_ids),
    )
    yield
    registry._channel_classes, registry._registered_class_ids = saved


class TestSetup:
    def test_start_up_registers_the_push_channel(self) -> None:
        assert registry.get_channel("push") is PushChannel

    def test_it_registers_the_channel_again_after_it_was_removed(
        self, restore_registry
    ) -> None:
        registry.unregister_channel(PushChannel)

        configure()

        assert registry.get_channel("push") is PushChannel

    def test_calling_it_twice_leaves_one_push_channel(self, restore_registry) -> None:
        configure()
        configure()

        keys = [channel.key for channel in registry.get_all_channels()]
        assert keys.count("push") == 1
