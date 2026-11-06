# Implementation Plan: Activity feeds and following

**Branch**: `002-activity-feeds-and-following` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

The pages and components Sam approved in the sketch are kept. Behind them go three views, one URLconf, two template tags and two menu entries. Every query, follow and unfollow is django-activity-stream's own. Nothing here has a model or a migration.

## Technical Context

- Python 3.12+, Django 5.2 to 6.1, django-mvp, django-cotton, daisy-cotton, uv.
- django-activity-stream 2.0 (the `activity` extra), `django.contrib.humanize`.
- Tests: pytest, pytest-django, rendering through the demo project.

## Constitution Check

- **XII Scope**: no models, no migrations. Every read and write is django-activity-stream's.
- **XIII Extras**: code that imports django-activity-stream lives in `mvp_community/integrations/activity/`. The tag library sits under `mvp_community/templatetags/`, where Django finds it, and imports django-activity-stream only inside each tag. The base-install test covers it.
- **XIV Templates before code**: the Python is wiring between the package and the templates.
- **VIII i18n**: every string is marked for translation.
- **I Testing**: test-first for each view, route, tag, menu entry and component behaviour. Wording and appearance are not tested.

## Design

### Package layout

```
mvp_community/
  apps.py                                   ready(): imports integrations.activity.menus when actstream is installed
  templatetags/mvp_community_activity.py    {% follower_count obj as n %}, {% followers_of obj as people %}
  integrations/activity/
    __init__.py
    urls.py                                 app_name "mvp_community_activity"
    views.py                                FeedView, FollowingView, FollowControlView
    menus.py                                AppMenu "activity_feed", AccountCenterMenu "following"
  templates/cotton/mvp_community/activity/  recent, feed, action, name, follow, followers, following_card
  templates/mvp_community/activity/         feed.html, following.html
  templates/mvp/account/overview.html       gains the following card, behind its URL guard
```

### Routes

| Name | Path | View |
|---|---|---|
| `feed` | `activity/` | `FeedView(LoginRequiredMixin, MVPListView)`, `paginate_by = 20`, queryset `Action.objects.user(request.user)` |
| `following` | `account-center/following/` | `FollowingView(LoginRequiredMixin, MVPListView)`, `paginate_by = 20`, queryset `Follow.objects.following_qs(request.user).order_by("-started")` |
| `follow_control` | `activity/control/<int:content_type_id>/<str:object_id>/` | `FollowControlView(View)`, GET only: resolves the object through `ContentType` (404 for an unknown type or object), renders the `follow` component alone. Its `next` query parameter, when it is a safe local path (`url_has_allowed_host_and_scheme`), is passed to the component as the page the plain form returns to |

The host includes both URLconfs: `path("", include("mvp_community.integrations.activity.urls"))` and, after it, `path("activity/", include("actstream.urls"))`. The package's `activity/` routes are matched first.

### The follow control

`cotton/mvp_community/activity/follow.html`, props `object`, `size`, `next` (defaults to the current page).

- The follower count as plain text beside one button: **Follow**, or **Unfollow** when the signed-in person follows the object. On a person's own control there is the count and no button. Signed out, Follow is a link to sign in carrying `next`.
- The count is `{% follower_count object as count %}`.
- The form posts to `{% follow_all_url object %}`, with `action` carrying `?next=<next>` for the fallback. It also carries `hx-post` to the same address with `?next=<the follow_control route for this object, itself carrying next>`, `hx-target` its own wrapper and `hx-swap="outerHTML"`. No `hx-boost`.
- The wrapper is the one element htmx replaces. It carries `data-follow-control` so a test and a host script can find it.

### Tags

`templatetags/mvp_community_activity.py`, each importing `actstream` inside the function:

- `follower_count obj` → `Follow.objects.followers_qs(obj).count()`.
- `followers_of obj` → `followers(obj)`, a queryset of users. The followers list takes the first eight and the count from `follower_count`.

### Components kept from the sketch

`recent.html` (props `object`, `following`, `verb`, `limit`, `more_url`, `more_text`), `feed.html`, `action.html`, `name.html`, `followers.html` (now counting with `follower_count`, slicing `followers_of`), `following_card.html`, and the two page templates. They are kept as approved and changed only where a task says.

### Demo and tests

- The demo keeps the sketch's wiring: `actstream` in `INSTALLED_APPS`, the registry call in `DemoConfig.ready()`, `ABSOLUTE_URL_OVERRIDES`, the people and group pages, the icons, both URL includes, `seed_activity`.
- Tests make activity with `actstream.action.send` and follows with `actstream.actions.follow`, never by writing rows by hand. Fixtures in `tests/conftest.py`: people (the existing user factory), a group, their actions and follows. `tests/settings.py` inherits the demo, so registration comes with it.
- Modules mirror the source: `tests/test_integrations/test_activity/test_views.py` and `test_menus.py`, `tests/test_templatetags/test_mvp_community_activity.py`, component behaviour in `tests/test_integrations/test_activity/test_components.py`, overrides in `tests/test_templates/test_overrides.py`.

### Documentation

`docs/developer/activity.md`: installing the extra, `INSTALLED_APPS`, both URL includes and their order, registering models with django-activity-stream, recording activity (pointing at its documentation, with `public`), `get_absolute_url`, the icon names (`activity`, `activity.follow`, `activity.unfollow`, `activity.following`), placing each component with its props, every template that can be overridden by name, and the known limitations: the follow view's missing CSRF check upstream, and three queries per follow control in a list. README's extras section links to it. `CHANGELOG.md` gets an Added entry. `CONTEXT.md` gains **recent activity** (D3). `locale/en/LC_MESSAGES/django.po` is regenerated.

### Story order

US1 → US2 → US3, one at a time in this working tree. US1 has two groups: the extra switched on with recent activity, then the followers list, overrides and documentation.

### The sketch's Python

Each group starts by deleting the sketch's Python it rebuilds (views, URLconf, menus, the `ready()` branch, the tag library), so every test is seen to fail before the code returns. Templates stay.
