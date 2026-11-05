"""The Account Center entry for notification preferences."""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import AccountCenterMenu

AccountCenterMenu.append(
    MenuItem(
        name="notification_preferences",
        view_name="mvp_community_notifications:preferences",
        extra_context={"label": _("Notifications"), "icon": "notifications"},
    )
)
