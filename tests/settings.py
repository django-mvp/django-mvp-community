"""Django settings for testing django-mvp-community."""

# Everything else is inherited from demo/settings.py rather than restated, so the
# suite cannot stay green against its own copy while the demo is broken.
from demo.settings import *  # noqa: F403

SECRET_KEY = "django-insecure-test-key-for-mvp_community-tests-only"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# The demo keeps a file on disk so its data survives a restart. A test run
# wants neither the file nor the history.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# The demo's routes, behind a urlconf of the suite's own so a test-only route
# has somewhere to go.
ROOT_URLCONF = "tests.urls"

# Templates that exist only to put something in one exact situation a test
# needs. They are not part of the demo project and are never distributed.
TEMPLATES[0]["DIRS"] = [BASE_DIR / "tests" / "templates"]  # noqa: F405

# A user model keyed by UUID, for the tests that swap it in with
# override_settings. Its table is created from the model, with no migration.
INSTALLED_APPS = [*INSTALLED_APPS, "tests.uuid_users"]  # noqa: F405
