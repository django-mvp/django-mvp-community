"""The address that turns notification email off, and what reading and following it does."""

from django.contrib.auth import get_user_model
from django.core import signing
from django.urls import reverse
from generic_notifications.registry import registry
from mvp.templatetags.mvp_email import EmailSite

from mvp_community.templatetags.mvp_community_notifications import UNSUBSCRIBE_SALT


def _always_emailed(notification_type):
    """Say whether the project sends this type by email whatever the person chooses."""
    return any(c.key == "email" for c in notification_type.required_channels)


class UnsubscribeLink:
    """Which person and which notification types an unsubscribe address turns off email for.

    The address is signed, so it needs no stored record, and it does not expire:
    RFC 8058 expects the header it goes in to keep working.

    Attributes:
        user: The person the email was sent to.
        type_keys: The keys of the notification types the address names.
    """

    def __init__(self, user, type_keys):
        """Name a person and the types.

        Args:
            user: The person the email is sent to.
            type_keys: The notification type keys.
        """
        self.user = user
        self.type_keys = sorted(set(type_keys))

    @classmethod
    def for_email(cls, user, type_keys):
        """Make the link for an email that carries these types.

        Args:
            user: The person the email is sent to.
            type_keys: The keys of the types the email carries.

        Returns:
            A link for the types a person can turn off, or None when every
            type is one the project always sends by email.
        """
        keys = [key for key in type_keys if not _always_emailed(registry.get_type(key))]
        return cls(user, keys) if keys else None

    @property
    def types(self):
        """The registered notification types the link names."""
        return [registry.get_type(key) for key in self.type_keys]

    @property
    def path(self):
        """The signed address on the site."""
        token = signing.dumps(
            {"u": self.user.pk, "t": self.type_keys}, salt=UNSUBSCRIBE_SALT
        )
        return reverse("mvp_community_notifications:unsubscribe", args=[token])

    def url(self, request=None):
        """Give the address with the site's host, for an email.

        Args:
            request: The request being answered, or None outside one.

        Returns:
            An absolute address.
        """
        return EmailSite.absolute(request, self.path)

    @classmethod
    def read(cls, token):
        """Read a token from an address.

        A type the project has since made always emailed is dropped, so an old
        link never turns off a type that has become required.

        Args:
            token: The signed token from the address.

        Returns:
            The link, or None when the signature is bad, the person no longer
            exists or no type it names is still registered and optional.
        """
        user_model = get_user_model()
        try:
            data = signing.loads(token, salt=UNSUBSCRIBE_SALT)
            user = user_model.objects.get(pk=data["u"])
            keys = [
                key
                for key in data["t"]
                if key in {t.key for t in registry.get_all_types()}
            ]
        except (signing.BadSignature, KeyError, TypeError, user_model.DoesNotExist):
            return None
        return cls.for_email(user, keys)

    def emailed(self):
        """Give the types among these that still reach the person by email."""
        return [
            t
            for t in self.types
            if "email" in [c.key for c in t.get_enabled_channels(self.user)]
        ]

    def turn_off(self):
        """Turn email off for each type that still reaches the person by it.

        Returns:
            The types changed.
        """
        email = registry.get_channel("email")
        changed = self.emailed()
        for notification_type in changed:
            notification_type.disable_channel(self.user, email)
        return changed
