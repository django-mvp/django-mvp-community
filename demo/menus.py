"""Sidebar navigation for the demo project, registered by ``DemoConfig.ready``."""

# A menu entry whose view_name will not resolve is dropped without an error, so a
# page missing from the sidebar is usually a name that does not match the route.
from flex_menu import MenuItem
from mvp.menus import AppMenu

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        MenuItem(
            name="people",
            view_name="people",
            extra_context={"label": "People and groups", "icon": "people"},
        ),
        MenuItem(
            name="site_activity",
            view_name="site_activity",
            extra_context={"label": "Site activity", "icon": "activity"},
        ),
    ]
)
