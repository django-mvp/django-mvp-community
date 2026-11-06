"""Factories for the suite's models."""

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


class GroupFactory(factory.django.DjangoModelFactory):
    """A group of people, which the demo lets a person follow."""

    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")
