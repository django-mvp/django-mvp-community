"""Factories for the suite's models."""

import base64

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class UserFactory(factory.django.DjangoModelFactory):
    """A person who can sign in."""

    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"person{n}@example.com")
    email = factory.LazyAttribute(lambda user: user.username)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # create_user hashes the password and saves once. A password set after
        # the save is never written, and the session hash then fails to match.
        kwargs.setdefault("password", "password")
        return cls._get_manager(model_class).create_user(*args, **kwargs)


class UUIDUserFactory(factory.django.DjangoModelFactory):
    """A person whose primary key is a UUID, as some host projects' user models have."""

    class Meta:
        model = "uuid_users.UUIDUser"

    email = factory.Sequence(lambda n: f"uuid{n}@example.com")


class GroupFactory(factory.django.DjangoModelFactory):
    """A group of people, which the demo lets a person follow."""

    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")


def urlsafe(data):
    """Encode bytes as a browser's push manager does: URL-safe, unpadded."""
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


# The shapes a browser sends: an uncompressed P-256 point and a 16-byte secret.
P256DH = urlsafe(b"\x04" + bytes(range(64)))
AUTH = urlsafe(bytes(range(16)))


class PushSubscriptionFactory(factory.django.DjangoModelFactory):
    """One browser a person turned push on in."""

    class Meta:
        model = "push_notifications.WebPushDevice"

    user = factory.SubFactory(UserFactory)
    registration_id = factory.Sequence(
        lambda n: f"https://fcm.googleapis.com/fcm/send/subscription-{n}"
    )
    p256dh = P256DH
    auth = AUTH
