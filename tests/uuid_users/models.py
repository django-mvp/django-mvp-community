"""A user model whose primary key is a UUID, as a host project may swap in."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UUIDUser(AbstractBaseUser):
    """A person whose primary key is a UUID rather than a number.

    It is never made the suite's ``AUTH_USER_MODEL``: a test that needs it
    swaps it in with ``override_settings``.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="id",
        help_text="The person's key.",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="email address",
        help_text="The address the person signs in with.",
    )

    USERNAME_FIELD = "email"

    objects = BaseUserManager()
