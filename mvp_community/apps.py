"""App configuration for django-mvp-community."""

from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class MvpCommunityConfig(AppConfig):
    """What a project gets when it adds this package to INSTALLED_APPS.

    The label is set explicitly rather than left to Django's default, which is
    the last segment of the module path. Two installed apps whose paths end in
    the same word collide on that default, and the error names neither of them
    clearly.
    """

    name = "mvp_community"
    label = "mvp_community"
    verbose_name = _("Community")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Add each installed extra's Account Center entry."""
        if apps.is_installed("generic_notifications"):
            from mvp_community.integrations.notifications import (
                checks,  # noqa: F401
                menus,  # noqa: F401
                setup,
            )

            setup.configure(apps.is_installed("post_office"))
        if apps.is_installed("generic_notifications") and apps.is_installed(
            "push_notifications"
        ):
            from mvp_community.integrations.push import (
                checks as push_checks,  # noqa: F401
            )
            from mvp_community.integrations.push import setup as push_setup

            push_setup.configure()
        if apps.is_installed("actstream"):
            from mvp_community.integrations.activity import (
                menus as activity,  # noqa: F401
            )
