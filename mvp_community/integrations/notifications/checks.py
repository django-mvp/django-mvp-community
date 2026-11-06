"""The system check that guards against naming the library's email channel."""

from django.core.checks import Error, register
from generic_notifications.channels import EmailChannel
from generic_notifications.registry import registry

from .channels import NotificationEmailChannel


@register()
def check_email_channel_named(app_configs, **kwargs):
    """Report each notification type that names the library's email channel.

    django-generic-notifications compares channel classes by identity, so a
    type naming its ``EmailChannel`` stops matching once this package's
    channel is registered under ``email``.

    Args:
        app_configs: The app configs being checked, which this check ignores.
        **kwargs: The other arguments Django passes to a check.

    Returns:
        One error for each type that names the library's class.
    """
    try:
        registered = registry.get_channel("email")
    except KeyError:
        return []
    if not issubclass(registered, NotificationEmailChannel):
        return []
    return [
        Error(
            f"The notification type {notification_type.__name__} names "
            "generic_notifications.channels.EmailChannel, which is not the "
            "registered email channel.",
            hint=(
                "Name mvp_community.integrations.notifications.channels."
                "NotificationEmailChannel instead."
            ),
            obj=notification_type,
            id="mvp_community.E001",
        )
        for notification_type in registry.get_all_types()
        if any(
            channel is EmailChannel
            for channel in [
                *notification_type.required_channels,
                *(notification_type.default_channels or []),
            ]
        )
    ]
