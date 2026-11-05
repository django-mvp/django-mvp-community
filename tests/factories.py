"""Factories for the suite's models."""

import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    """A person who can sign in."""

    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"person{n}@example.com")
    email = factory.LazyAttribute(lambda user: user.username)
    password = factory.PostGenerationMethodCall("set_password", "password")
