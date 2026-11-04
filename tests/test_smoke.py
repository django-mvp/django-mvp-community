"""The package installs and exposes what a consuming project needs from it."""

import subprocess
import sys
from importlib import metadata
from pathlib import Path

from django.apps import apps
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

import mvp_community

PACKAGE_ROOT = Path(mvp_community.__file__).parent
COTTON_ROOT = PACKAGE_ROOT / "templates" / "cotton" / "mvp_community"

EXAMPLE_TAG = "c-mvp_community.example"

# A fresh interpreter, so nothing the suite imported can satisfy the import. A
# name set to None in sys.modules raises ImportError on import, which blocks an
# extra's packages even where they are installed, as they are for development.
IMPORT_WITHOUT_EXTRAS = """
import importlib
import pkgutil
import sys

for name in sys.argv[1:]:
    sys.modules[name] = None

import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "mvp_community",
    ]
)
django.setup()

import mvp_community

for module in pkgutil.walk_packages(mvp_community.__path__, "mvp_community."):
    if not module.name.startswith("mvp_community.integrations."):
        importlib.import_module(module.name)
"""


def extra_import_names() -> list[str]:
    """Find the import names of the installed packages that extras bring.

    Returns:
        The top-level import names, sorted. An extra's package that is not
        installed has none, and cannot be imported anyway.
    """
    extra_packages = {
        canonicalize_name(requirement.name)
        for requirement in map(
            Requirement, metadata.requires("django-mvp-community") or []
        )
        if requirement.marker is not None and "extra" in str(requirement.marker)
    }
    return sorted(
        name
        for name, distributions in metadata.packages_distributions().items()
        if extra_packages & {canonicalize_name(d) for d in distributions}
    )


class TestPackagedApp:
    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_community")

    def test_components_are_where_cotton_looks_for_them(self) -> None:
        # The directory name is the first segment of every tag, and a component
        # Cotton cannot find renders as empty output rather than raising.
        assert COTTON_ROOT.is_dir()


class TestBaseInstall:
    def test_every_module_outside_the_integrations_imports_without_extras(
        self,
    ) -> None:
        # Only mvp_community.integrations may import an extra's packages. A
        # module anywhere else that does breaks every project installed
        # without that extra.
        result = subprocess.run(  # noqa: S603 - fixed script, this interpreter
            [sys.executable, "-c", IMPORT_WITHOUT_EXTRAS, *extra_import_names()],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr


class TestStarterComponent:
    # Delete this class along with the starter component it covers.

    def test_it_renders_its_slot(self, render) -> None:
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "Inside" in markup

    def test_it_renders_a_title_when_given_one(self, render) -> None:
        markup = render(f'<{EXAMPLE_TAG} title="Named" />')
        assert "Named" in markup

    def test_it_renders_no_heading_without_a_title(self, render) -> None:
        # Asserted as an absence: a component that always drew the heading would
        # pass the test above while putting an empty one on every page.
        markup = render(f"<{EXAMPLE_TAG}>Inside</{EXAMPLE_TAG}>")
        assert "<h2" not in markup
