"""The email channel the notifications extra registers in place of the library's."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import translation
from generic_notifications.channels import EmailChannel
from generic_notifications.registry import registry


class NotificationEmailChannel(EmailChannel):
    """Notification email, written in the recipient's language and queued by the mail extra.

    Rendering is the library's. This class sets the language it renders in,
    sends a type that is always emailed at once, and sends through Django's
    mail backend, so django-post-office queues and logs each email.

    Attributes:
        unsubscribe_link: The link the email being sent carries, or None when
            it carries none.
    """

    unsubscribe_link = None

    def process(self, notification):
        """Send a type the project always emails at once, whatever frequency is stored.

        Args:
            notification: The notification to process.
        """
        if registry.get_type(notification.notification_type).required_channels:
            self.send_now(notification)
            return
        super().process(notification)

    def recipient_language(self, user):
        """Give the language the person's email is written in.

        Django has no language per person, so this is the site's. A project
        that stores one overrides this.

        Args:
            user: The person the email is sent to.

        Returns:
            A language code.
        """
        return settings.LANGUAGE_CODE

    def send_now(self, notification):
        """Send one notification in the recipient's language.

        Args:
            notification: The notification to send.
        """
        self.unsubscribe_link = None
        with translation.override(self.recipient_language(notification.recipient)):
            super().send_now(notification)

    def send_digest(self, notifications, frequency):
        """Send a digest in the recipient's language.

        Args:
            notifications: The notifications to include, all for one person.
            frequency: The digest's frequency class.
        """
        self.unsubscribe_link = None
        first = notifications.first()
        if first is None:
            return
        with translation.override(self.recipient_language(first.recipient)):
            super().send_digest(notifications, frequency)

    def email_headers(self):
        """Give the headers the email being sent carries.

        Returns:
            A dict of header names to values.
        """
        return {}

    def send_email(self, recipient, subject, text_message, html_message=None):
        """Send the email through Django's mail backend.

        Args:
            recipient: The address to send to.
            subject: The subject line.
            text_message: The plain text body.
            html_message: The HTML body, when there is one.
        """
        message = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            headers=self.email_headers(),
        )
        if html_message:
            message.attach_alternative(html_message, "text/html")
        message.send(fail_silently=False)
