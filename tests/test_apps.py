"""The app configuration wires in an extra only where the extra is installed."""

import subprocess
import sys

MENUS_MODULE = "mvp_community.integrations.notifications.menus"

# A fresh interpreter: what ready() imported in this one says nothing about a
# project that did not install the extra.
IMPORT_MENUS_AFTER_SETUP = f"""
import sys

import django
from django.conf import settings

apps = ["django.contrib.auth", "django.contrib.contenttypes", "mvp_community"]
apps += sys.argv[1:]
settings.configure(INSTALLED_APPS=apps)
django.setup()

print("{MENUS_MODULE}" in sys.modules)
"""


def menus_imported_with(*extra_apps: str) -> str:
    result = subprocess.run(  # noqa: S603 - fixed script, this interpreter
        [sys.executable, "-c", IMPORT_MENUS_AFTER_SETUP, *extra_apps],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


class TestMvpCommunityConfig:
    def test_it_registers_the_notifications_menu_when_the_extra_is_installed(
        self,
    ) -> None:
        assert (
            menus_imported_with("mvp", "flex_menu", "generic_notifications") == "True"
        )

    def test_it_leaves_the_notifications_menu_alone_without_the_extra(self) -> None:
        assert menus_imported_with() == "False"
