"""What the notifications extra registers with django-generic-notifications."""

from generic_notifications.channels import EmailChannel
from generic_notifications.registry import registry
from generic_notifications.types import SystemMessage

from .channels import NotificationEmailChannel
from .frequencies import WeeklyFrequency


def configure(mail_installed):
    """Register the extra's frequency and channel, and remove the library's own type.

    Every registration is forced, because the registry skips a class it has
    seen before, so without it this could not be called twice.

    Args:
        mail_installed: Whether the mail extra is installed. Without it no
            email channel is registered and the site is the only channel.
    """
    registry.register_frequency(WeeklyFrequency, force=True)
    registry.unregister_type(SystemMessage)
    registry.unregister_channel(EmailChannel)
    if mail_installed:
        registry.register_channel(NotificationEmailChannel, force=True)
