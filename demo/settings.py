"""Settings for the demo project, a demonstration target that is never deployed."""

import os
from pathlib import Path

from py_vapid import Vapid01
from py_vapid.utils import b64urlencode

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-project-only"

DEBUG = True

# The development server is reached over the network by hostname, not only at
# localhost. DEBUG auto-allows localhost and nothing else, so a bare list here
# answers any other hostname with 400 Bad Request.
ALLOWED_HOSTS = ["*"]

# The development server speaks plain HTTP. A cookie marked Secure is discarded
# by the browser, which leaves GET pages rendering perfectly while every form
# post comes back 403.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Own apps first so demo/templates/base.html wins over the libraries' copies.
# A template here named after one django-mvp ships replaces it everywhere.
INSTALLED_APPS = [
    "demo",
    "mvp_community",
    # The notifications extra: the package it is built on.
    "generic_notifications",
    "actstream",
    # The push extra: the package it is built on, with its own migrations.
    "push_notifications",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    # The notifications page says when each one arrived as "2 hours ago".
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "mvp",
    # The components django-mvp's own templates are built from. Below "mvp",
    # so a component both of them have is django-mvp's.
    "daisy_cotton",
    "easy_icons",
    "crispy_forms",
    "mvp_forms",
    "flex_menu",
    "django_cotton",
    # The mail extra: the queue, the delivery log and the stored templates.
    "post_office",
    # Reloads the browser on a change to a template, a stylesheet or Python. It
    # arrives with the shared development bundle rather than a pin of its own,
    # and its middleware removes itself from the chain unless DEBUG is on.
    "django_browser_reload",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # The shell puts the site's name in every page title, reading it from
    # request.site. This middleware is what puts it there.
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Last, because it rewrites the response body to insert its script tag and
    # anything that encodes or compresses the body has to run after it.
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mvp.context_processors.mvp_config",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict] = []

# The sign-in page django-mvp's URLs register. Django's default, /accounts/login/,
# is an address nothing here serves.
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]
CRISPY_TEMPLATE_PACK = "daisyui"

# Which class draws the sidebar tree declared in demo/menus.py, and which draws
# the dock shown below the sidebar breakpoint.
FLEX_MENUS = {
    "renderers": {
        "sidebar": "mvp.renderers.SidebarRenderer",
        "dock": "mvp.renderers.MobileFooterNavRenderer",
    },
    "log_url_failures": DEBUG,
}

# Icons are referenced by name. django-mvp's pack covers the names the shell
# uses for itself; anything this project names goes on top of it. An
# unregistered name raises rather than drawing nothing.
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "packs": ["mvp.utils.BS5_ICONS"],
        "icons": {
            "overview": "bi bi-house",
            "notifications": "bi bi-bell",
            "notifications.preferences": "bi bi-sliders",
            "notifications.push": "bi bi-phone-vibrate",
            "notifications.push.phone": "bi bi-phone",
            "notifications.push.tablet": "bi bi-tablet",
            "notifications.push.computer": "bi bi-laptop",
            "activity": "bi bi-activity",
            "activity.follow": "bi bi-plus-lg",
            "activity.following": "bi bi-check2",
            "activity.unfollow": "bi bi-x-lg",
            "people": "bi bi-people",
        },
    },
}

# Deep-merged over django-mvp's defaults, so only the differences appear here.
MVP_CONFIG = {
    "layout": {
        "sidebar": {
            "title": "django-mvp-community",
        },
        "navbar": {
            "end": [
                "mvp_community.notifications.bell",
                "mvp.actions.theme-controller",
                "mvp.actions.login",
            ],
        },
    },
    "theme": {
        # Several to switch between, so what this package renders can be looked
        # at light and dark without editing a setting.
        "choices": ["light", "dark", "corporate", "dracula"],
    },
}

STATIC_URL = "/static/"

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The mail extra: every email is queued and logged, then handed to the backend
# below. SMTP when DEMO_EMAIL_HOST is set (a Mailpit inbox, for instance), the
# console otherwise, so the demo needs no mail server.
EMAIL_BACKEND = "post_office.EmailBackend"

# django-post-office clears a different cache key than the one it reads when a
# translation is saved, so a cached template would ignore a staff edit.
POST_OFFICE_TEMPLATE_CACHE = False

POST_OFFICE = {
    # Sent during the call, so the demo needs no queue runner.
    "DEFAULT_PRIORITY": "now",
    "BACKENDS": {
        "default": (
            "django.core.mail.backends.smtp.EmailBackend"
            if os.environ.get("DEMO_EMAIL_HOST")
            else "django.core.mail.backends.console.EmailBackend"
        ),
    },
}
EMAIL_HOST = os.environ.get("DEMO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("DEMO_EMAIL_PORT", "1025"))

# django-activity-stream links each actor and object through get_absolute_url.
# The demo's people and groups are Django's own models, so their pages are
# named here instead.
ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda user: f"/people/{user.pk}/",
    "auth.group": lambda group: f"/groups/{group.pk}/",
}

# The push extra. The signing key is made when this file is imported and kept in
# memory only, so nothing is written to disk. A restart gives a new key, which
# retires the demo's earlier push subscriptions: the push services refuse a
# message signed with a different key. A real project sets a key of its own.
_vapid = Vapid01()
_vapid.generate_keys()
PUSH_NOTIFICATIONS_SETTINGS = {
    "WP_PRIVATE_KEY": b64urlencode(
        _vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    ),
    "WP_CLAIMS": {"sub": "mailto:admin@example.com"},
}
