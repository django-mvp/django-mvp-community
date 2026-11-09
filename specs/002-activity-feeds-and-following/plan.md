# Implementation Plan: Activity feeds and following

**Branch**: `002-activity-feeds-and-following` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

The pages and components Sam approved in the sketch are kept. Behind them go one configurable feed view the host mounts itself, two built-in views, one URLconf, one template tag and one menu entry. Every query, follow and unfollow is django-activity-stream's own. Nothing here has a model or a migration.

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
  templatetags/mvp_community_activity.py    {% followers_of obj as people %}
  integrations/activity/
    __init__.py
    urls.py                                 app_name "mvp_community_activity"
    views.py                                ActivityFeedView (mounted by the host), FollowingView, FollowControlView
    menus.py                                AccountCenterMenu "following"
  templates/cotton/mvp_community/activity/  recent, feed, action, name, follow, followers, following_card
  templates/mvp_community/activity/         feed.html, following.html
  templates/mvp/account/overview.html       gains the following card, behind its URL guard
```

### Routes

| Name | Path | View |
|---|---|---|
| `following` and the routes below | | the package's own. **No feed route**: the host mounts `ActivityFeedView` itself (below) |
| `following` | `account/following/` | `FollowingView(LoginRequiredMixin, MVPListView)`, `paginate_by = 20`, queryset `Follow.objects.following_qs(request.user).order_by("-started")` |
| `follow_control` | `activity/control/<int:content_type_id>/<str:object_id>/` | `FollowControlView(LoginRequiredMixin, View)`, GET only: resolves the object through `ContentType`, 404 for an unknown type, an unknown object or a model not registered with django-activity-stream, and renders the `follow` component alone. Its `next` query parameter, when it is a safe local path (`url_has_allowed_host_and_scheme`), is passed to the component as the page the plain form returns to |
| `actstream_follow`, `actstream_follow_all`, `actstream_unfollow`, `actstream_unfollow_all` | under `activity/` | django-activity-stream's own four follow patterns, taken from `actstream.urls.urlpatterns` by name. Nothing else of `actstream.urls` is mounted: its `detail/` view shows actions that are not public and its `following/` view shows anyone's follows, to anyone |

The host includes one URLconf: `path("", include("mvp_community.integrations.activity.urls"))` (SC-001).

### The feed view

`ActivityFeedView(MVPListView)`, `template_name = "mvp_community/activity/feed.html"`, `paginate_by = 20`. Configured by class attribute or `as_view()` argument:

- `stream`: `"following"` (default), `"site"` or `"object"`. Each maps to django-activity-stream's own manager method: `user`, `public`, `any`.
- `verb`: when set, passed to that method as `verb=`.
- `get_stream_object()`: returns the object for `"object"`. The default raises `ImproperlyConfigured`; the host overrides it, usually from the URL's kwargs.
- `"following"` requires a signed-in person (redirect to sign in, as `LoginRequiredMixin` does) and excludes the person's own actions. The other two are open.
- Page title and lead are the host's, through `MVPListView`'s own `page_title` and `page_lead`; the defaults read "Activity".

```python
path("activity/", ActivityFeedView.as_view(), name="activity"),
path("activity/finished/", ActivityFeedView.as_view(stream="site", verb="finished")),
```

The demo mounts it three times: following (in its sidebar), the whole site, and one group's activity.

### The follow control

`cotton/mvp_community/activity/follow.html`, props `object`, `size`, `next` (defaults to the current page).

- The follower count as plain text beside one button: **Follow**, or **Unfollow** when the signed-in person follows the object. On a person's own control there is the count and no button. Signed out, Follow is a link to sign in carrying `next`.
- The count is `{% followers_of object as followers %}` then `followers.count`.
- On the following page the control is given `replace_row`: its htmx target is the row, so stopping following removes the row (spec US3 scenario 2).
- The form posts to `{% follow_all_url object %}`, with `action` carrying `?next=<next>` for the fallback. It also carries `hx-post` to the same address with `?next=<the follow_control route for this object, itself carrying next>`, `hx-target` its own wrapper and `hx-swap="outerHTML"`. No `hx-boost`.
- The wrapper is the one element htmx replaces. It carries `data-follow-control` so a test and a host script can find it.

### Tags

`templatetags/mvp_community_activity.py`, each importing `actstream` inside the function:

- `followers_of obj` → `followers(obj)`, a queryset of users. The count is its `.count`, one `COUNT` query; the followers list slices the first eight.

### Components kept from the sketch

`recent.html` (guards `following` for a signed-out visitor: no activity, no error) (props `object`, `following`, `verb`, `limit`, `more_url`, `more_text`), `feed.html`, `entry.html` (the sketch's `action.html`, renamed: the glossary keeps "action" for django-activity-stream's model), `name.html`, `followers.html` (counting and slicing `followers_of`), `following_card.html`, and the two page templates. They are kept as approved and changed only where a task says.

### Demo and tests

- The demo keeps the sketch's wiring: `actstream` in `INSTALLED_APPS`, the registry call in `DemoConfig.ready()`, `ABSOLUTE_URL_OVERRIDES`, the people and group pages, the icons, both URL includes, `seed_activity`.
- Tests make activity with `actstream.action.send` and follows with `actstream.actions.follow(..., actor_only=False)`, as the control does, never by writing rows by hand. Fixtures in `tests/conftest.py`: people (the existing user factory), a group (a new `GroupFactory`), their actions and follows. `tests/settings.py` inherits the demo, so registration comes with it.
- Modules mirror the source: `tests/test_integrations/test_activity/test_views.py` and `test_menus.py`, `tests/test_templatetags/test_mvp_community_activity.py`, component behaviour in `tests/test_integrations/test_activity/test_components.py`, overrides in `tests/test_templates/test_overrides.py`.

### Documentation

`docs/developer/activity.md`: installing the extra, `INSTALLED_APPS`, both URL includes and their order, registering models with django-activity-stream, recording activity (pointing at its documentation, with `public`), `get_absolute_url`, the icon names (`activity`, `activity.follow`, `activity.unfollow`, `activity.following`), placing each component with its props, every template that can be overridden by name, that `django.contrib.auth.context_processors.auth` is required, and the known limitations of django-activity-stream's follow view: no CSRF check, it follows on a plain GET, and it redirects to any `next` without checking it; and three queries per follow control in a list. Mounting the feed view with each `stream`, and adding it to a menu, is documented with the two lines it takes. README's extras section links to it. `CHANGELOG.md` gets an Added entry. `CONTEXT.md` gains **recent activity** (D3). `locale/en/LC_MESSAGES/django.po` is regenerated.

### Story order

US1 → US2 → US3, one at a time in this working tree. US1 has two groups: the extra switched on with recent activity, then the followers list, overrides and documentation.

### The sketch's Python

Each group starts by deleting the sketch's Python it rebuilds (views, URLconf, menus, the `ready()` branch, the tag library), so every test is seen to fail before the code returns. Templates stay.
