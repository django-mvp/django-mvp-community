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
        """Add each installed extra's menu entries."""
        if apps.is_installed("generic_notifications"):
            from mvp_community.integrations.notifications import menus  # noqa: F401
        if apps.is_installed("actstream"):
            from mvp_community.integrations.activity import menus as activity  # noqa: F401
