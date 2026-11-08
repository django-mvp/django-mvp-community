"""What the push extra registers with django-generic-notifications."""

from generic_notifications.registry import registry

from .channels import PushChannel


def configure():
    """Register the push channel.

    The registration is forced, because the registry skips a class it has seen
    before, so without it this could not be called twice.
    """
    registry.register_channel(PushChannel, force=True)
