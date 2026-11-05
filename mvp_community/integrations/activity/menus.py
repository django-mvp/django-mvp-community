"""The sidebar entry for the feed and the Account Center entry for following."""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import AccountCenterMenu, AppMenu

AppMenu.append(
    MenuItem(
        name="activity_feed",
        view_name="mvp_community_activity:feed",
        extra_context={"label": _("Feed"), "icon": "activity"},
    )
)

AccountCenterMenu.append(
    MenuItem(
        name="following",
        view_name="mvp_community_activity:following",
        extra_context={"label": _("Following"), "icon": "activity.following"},
    )
)
