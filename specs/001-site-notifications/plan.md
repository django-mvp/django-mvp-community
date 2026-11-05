# Implementation Plan: Notifications on the site

**Branch**: `001-site-notifications` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

The pages Sam approved in the sketch are kept as they are: the bell, the notification row, the notifications page, the preferences page and the Account Center card, all under `mvp_community/templates/`. Behind them go four small views, one URLconf, one template tag and one menu entry, all calling django-generic-notifications for every read and write. Nothing here has a model or a migration.

## Technical Context

- Python 3.12+, Django 5.2 to 6.1, django-mvp, django-cotton, daisy-cotton, uv.
- django-generic-notifications 2.4 (the `notifications` extra), `django.contrib.humanize`.
- Tests: pytest, pytest-django, rendering through the demo project, as the suite already does.

## Constitution Check

- **XII Scope**: no models, no migrations. Every read and write is the package's own function.
- **XIII Extras**: code that imports django-generic-notifications lives in `mvp_community/integrations/notifications/`. The one exception the layout forces is the tag library, which Django only finds under `mvp_community/templatetags/`; it imports nothing from the extra at module level, and the existing base-install test covers it (D2).
- **XIV Templates before code**: the Python is the wiring between the package and the templates, nothing else.
- **VIII i18n**: every string is marked for translation.
- **I Testing**: test-first for every view, the tag, the menu entry and the card.

## Design

### Package layout

```
mvp_community/
  apps.py                               ready(): registers the Account Center entry when generic_notifications is installed
  templatetags/mvp_community_notifications.py   {% notifications_unread_count as count %}
  integrations/notifications/
    __init__.py
    urls.py                             app_name "mvp_community_notifications"
    views.py                            NotificationListView, OpenNotificationView, MarkAllReadView, BellView, PreferencesView
    menus.py                            AccountCenterMenu entry "notification_preferences"
  templates/                            as approved in the sketch
```

### Routes

| Name | Path | View |
|---|---|---|
| `list` | `notifications/` | `NotificationListView(LoginRequiredMixin, MVPListView)`, `paginate_by = 20`, queryset `get_notifications(request.user)` |
| `open` | `notifications/<int:pk>/` | `OpenNotificationView(LoginRequiredMixin, View)`: the person's own notification only (404 otherwise), marks it read, redirects to its `url`, or to the list when it has none |
| `mark_all_read` | `notifications/read/` | `MarkAllReadView(LoginRequiredMixin, View)`: POST only. Marks the person's unread **site** notifications read with `get_notifications(user, unread_only=True).update(read=now)`, never `mark_notifications_as_read`, which also marks email-only ones read and would stop their digest. Redirects to the list |
| `bell` | `notifications/bell/` | `BellView(View)`: renders the bell alone for its own refresh. **A signed-out request gets 204 and no body**, never a redirect: htmx would follow a redirect and swap the sign-in page into the header, and the spec's edge case keeps the last count |
| `preferences` | `account-center/notifications/` | `PreferencesView(LoginRequiredMixin, MVPTemplateView)`: GET draws the grid, POST saves it, adds a success message and redirects back |

The page views use django-mvp's `MVPListView` and `MVPTemplateView`, which supply the `page` context both templates read (title, lead, breadcrumbs). Nothing builds page context by hand.

The host includes the URLconf at the root: `path("", include("mvp_community.integrations.notifications.urls"))`.

### The bell

`cotton/mvp_community/notifications/bell.html` takes its count from `{% notifications_unread_count as count %}`, which reads `request.user` from the context and returns the site-channel unread count, or nothing for a signed-out visitor. It links to the notifications page. It refreshes itself every 60 seconds with `hx-get` on the `bell` route and on a `notifications:changed` event, swapping its own outer element. The sketch's `notifications_unread` context variable goes.

### Demo and tests

- `demo/settings.py`: `generic_notifications` and `django.contrib.humanize` in `INSTALLED_APPS`, the bell first in `navbar.end`, icons `notifications` (`bi bi-bell`) and `notifications.preferences` (`bi bi-sliders`), and a console email backend.
- `demo/urls.py`: the include at the root.
- `demo/notifications.py`: the four demo types, imported from `DemoConfig.ready()`.
- `demo/management/commands/seed_notifications.py`: as in the sketch, DEBUG only.
- The overview page's "Send me a notification" section, as in the sketch.
- The sketch's Python is kept for reference in the run record; it is rebuilt here test-first.
- Tests make notifications with `generic_notifications.send_notification`, never by hand-writing rows the package would not write. Fixtures in `tests/conftest.py`: a person (a user factory in `tests/factories.py`) and their notifications. Test modules hold assertions, not construction.
- Test modules mirror the source: `tests/test_integrations/test_notifications/test_views.py` and `test_menus.py`, `tests/test_templatetags/test_mvp_community_notifications.py`, `tests/test_apps.py`, each subpackage with `__init__.py`. The template-override tests go in `tests/test_templates/`, declared in `pyproject.toml` under `[tool.forge.conformance] non-mirror-paths`.

### Documentation

`docs/developer/notifications.md`: installing the extra, the four settings lines, the URL include, the icon names, declaring a type and sending a notification (pointing at django-generic-notifications for that), the templates and components that can be overridden, by name. It says the type and channel names come from django-generic-notifications and are shown as it gives them. The README's extras section links to it and drops "no feature has been built yet" for this extra. `CHANGELOG.md` gets an Added entry under Unreleased. `mvp_community/locale/en/LC_MESSAGES/django.po` is generated with `makemessages` as the base English catalogue (Article VIII).

### Story order

US2 → US3 → US1, one at a time, in this working tree. US2 builds the pages US1 then switches on and documents. Each story is one dispatch group.

### The Account Center card

The card's markup moves, unchanged, into the component `cotton/mvp_community/notifications/preferences_card.html`. The package's `mvp/account/overview.html` keeps its URL guard and places `<c-mvp_community.notifications.preferences_card />`, so a project replaces the card by overriding that one component.
