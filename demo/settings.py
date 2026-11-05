"""Settings for the demo project, a demonstration target that is never deployed."""

from pathlib import Path

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

# Notifications also go out by email. The demo prints them to the console
# instead of reaching for a mail server it does not have.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
