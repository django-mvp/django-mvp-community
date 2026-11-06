# Tasks — 002 Activity feeds and following

**Branch**: `002-activity-feeds-and-following` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass, the tree is green and the work is committed. The templates approved in the sketch are kept: change one only where a task says so.

## Order

US1 → US2 → US3, one at a time (plan, *Story order*).

---

## Phase 1: User Story 1 — A developer turns activity on and places feeds and follow controls (P1)

Issue: #14. Delivers FR-001, FR-002, FR-005 to FR-009, FR-011, FR-012, FR-014, FR-015.

### Group 1

- [ ] T001 [US1] The activity extra is switched on

**Files**: `mvp_community/apps.py`, `mvp_community/integrations/activity/__init__.py`, `urls.py`, `views.py`, `menus.py`, `tests/conftest.py`, `tests/test_apps.py`, `tests/test_integrations/test_activity/__init__.py`, `tests/test_integrations/test_activity/test_menus.py`, `tests/test_smoke.py` only if the base-install test needs the new module named

Delete the sketch's Python first. `ready()` imports the menus when `actstream` is installed. The URLconf with the `following` route (a stub until US3) and django-activity-stream's four follow routes. No feed route. Fixtures: people, a group, actions (public and not), follows. Tests: the Account Center menu has the following entry, resolving; the package adds no sidebar entry and no feed route; the base install imports no `actstream` module.

- [ ] T002 [US1] Recent activity

**Files**: `mvp_community/templates/cotton/mvp_community/activity/recent.html`, `feed.html`, `entry.html` (renamed from `action.html`), `name.html`, `tests/test_integrations/test_activity/test_components.py`

Tests (rendered through a template string): the whole site's public activity, newest first, and none that is not public; around one object, only actions where it is actor, target or action object; `following` shows only what the signed-in person follows, and nothing for a signed-out visitor; `verb` limits to that kind; `limit` caps the rows; the link to `more_url` is present only when given and there is more than `limit`; nothing to show draws the empty state; a name links to `get_absolute_url` where the model has one and is plain otherwise; an action whose target was deleted is not shown; model data is escaped.

- [ ] T002a [US1] The feed view, for the whole site and one object

**Files**: `mvp_community/integrations/activity/views.py`, `mvp_community/templates/mvp_community/activity/feed.html`, `demo/urls.py`, `demo/menus.py`, `demo/views.py`, `tests/urls.py`, `tests/test_integrations/test_activity/test_views.py`

`ActivityFeedView` per plan, *The feed view*, with `stream` `"site"` and `"object"` and `verb`. The demo mounts it for the whole site and for a group. Tests: `"site"` lists the site's public activity newest first, open to a signed-out visitor; `"object"` lists only activity around the object from `get_stream_object()`; with no override, `"object"` raises `ImproperlyConfigured`; `verb` limits to that kind; 20 a page and page 2 holds the rest; the same number of queries for one action and for several.

### Group 2

- [ ] T003 [US1] The followers list and the follower tags

**Files**: `mvp_community/templatetags/mvp_community_activity.py`, `mvp_community/templates/cotton/mvp_community/activity/followers.html`, `tests/test_templatetags/test_mvp_community_activity.py`, `tests/test_integrations/test_activity/test_components.py`

`followers_of`, importing inside the tag. Tests: the count is the number of follows of that object; counting issues one query; the list shows the first eight followers and says how many more; none draws the empty state; `plain` leaves out the heading.

- [ ] T004 [US1] Any template can be replaced, and the documentation

**Files**: `tests/templates/…`, `tests/test_templates/test_overrides.py`, `docs/developer/activity.md`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `mvp_community/locale/en/LC_MESSAGES/django.po`

Tests: overriding each of the nine templates (`recent`, `feed`, `entry`, `name`, `follow`, `followers`, `following_card`, `feed.html`, `following.html`) uses the project's template and leaves the rest. Documentation per plan, *Documentation*.

---

## Phase 2: User Story 2 — A person follows people and things and sees their activity (P1)

Issue: #15. Delivers FR-003, FR-004, FR-005, FR-011, FR-012, FR-013.

### Group 1

- [ ] T005 [US2] The follow control

**Files**: `mvp_community/templates/cotton/mvp_community/activity/follow.html`, `mvp_community/templatetags/mvp_community_activity.py` (read only), `views.py`, `urls.py`, `tests/test_integrations/test_activity/test_views.py`, `tests/test_integrations/test_activity/test_components.py`

The component as plan, *The follow control*, and `FollowControlView` with the `follow_control` route. Tests: not following → the form posts to the follow address and the button is Follow; following → the stop-following address, Unfollow; the count is shown; signed out → a link to sign in carrying `next`; a person's own control has no form; the form carries `hx-post` to the follow address whose `next` is the control route, and the fallback `action` whose `next` is the page; `data-follow-control` on the wrapper; posting to django-activity-stream's follow address with that `next` and following the redirect returns the control showing Unfollow and the count one higher, and the reverse; the control route redirects a signed-out request to sign in and 404s for an unknown type, an unknown object or an unregistered model; only the four follow routes of django-activity-stream resolve under `activity/`; an off-site `next` is replaced by nothing.

- [ ] T006 [US2] The feed of what a person follows

**Files**: `views.py`, `demo/urls.py`, `demo/menus.py`, `tests/test_integrations/test_activity/test_views.py`

`stream="following"` on `ActivityFeedView` (the default), mounted by the demo in its sidebar. Tests: signed out redirects to sign-in; lists public activity of what the person follows, newest first, and nothing else; after unfollowing, new activity of that person does not appear; following someone records a public "started following" action, and the follower's own feed page does not show it; following nothing draws the empty state; 20 a page and page 2 holds the rest; the same number of queries for one action and for several.

---

## Phase 3: User Story 3 — A person reviews and trims what they follow (P2)

Issue: #16. Delivers FR-010, FR-012, FR-013.

### Group 1

- [ ] T007 [US3] The following page and its card

**Files**: `views.py`, `mvp_community/templates/mvp_community/activity/following.html`, `mvp_community/templates/cotton/mvp_community/activity/following_card.html`, `mvp_community/templates/mvp/account/overview.html`, `tests/test_integrations/test_activity/test_views.py`, `tests/test_integrations/test_activity/test_menus.py`

`FollowingView` per plan. Tests: signed out redirects; lists everything the person follows, newest first, each linking to its page where it has one; each row carries a follow control showing Unfollow, and stopping following through it removes the row; following nothing draws the empty state; 20 a page; the Account Center landing page has the following card linking to the page, and a project without the activity URLs gets no card.

---

## Review fixes

- [x] T008 [US1] Recent activity of what a person follows leaves out their own actions, as the feed view does
- [x] T009 [US1] The demo's overview links to its mounted feed
- [x] T010 [US1] Flagged follows are documented
- [x] T011 [US2] The follow form sends its CSRF token
- [x] T012 [US2] The test of the control's default return address uses a page other than the fallback
