"""The email channel the notifications extra registers in place of the library's."""

from generic_notifications.channels import EmailChannel


class NotificationEmailChannel(EmailChannel):
    """Notification email, sent through whatever mail backend the project sets up."""
