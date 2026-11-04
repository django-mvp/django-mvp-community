"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_community

PACKAGE_ROOT = Path(mvp_community.__file__).parent
COTTON_ROOT = PACKAGE_ROOT / "templates" / "cotton" / "mvp_community"

EXAMPLE_TAG = "c-mvp_community.example"


class TestPackagedApp:
    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_community")

    def test_components_are_where_cotton_looks_for_them(self) -> None:
        # The directory name is the first segment of every tag, and a component
        # Cotton cannot find renders as empty output rather than raising.
        assert COTTON_ROOT.is_dir()


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
