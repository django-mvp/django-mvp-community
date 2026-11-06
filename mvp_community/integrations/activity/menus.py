"""The Account Center entry for the page listing what a person follows."""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import AccountCenterMenu

AccountCenterMenu.append(
    MenuItem(
        name="following",
        view_name="mvp_community_activity:following",
        extra_context={"label": _("Following"), "icon": "activity.following"},
    )
)
