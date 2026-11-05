# Tasks — 001 Notifications on the site

**Branch**: `001-site-notifications` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md)

Every task follows the red-green-refactor cycle of Article I. A task is done when its tests pass, the tree is green and the work is committed. The templates approved in the sketch are kept: change one only where a task says so.

## Order

US2 → US3 → US1, one at a time (plan, *Story order*).

---

## Phase 1: User Story 2 — A person sees and reads their notifications (P1)

Issue: #10. Delivers FR-003 to FR-008, FR-013.

### Group 1

- [ ] T001 [US2] The demo can send notifications

**Files**: `demo/settings.py`, `demo/notifications.py`, `demo/apps.py`, `demo/urls.py`, `demo/management/commands/seed_notifications.py`, `tests/test_demo.py`

As plan, *Demo and tests*. Test: a demo notification type is registered.

- [ ] T002 [US2] The notifications page

**Files**: `mvp_community/integrations/__init__.py`, `mvp_community/integrations/notifications/__init__.py`, `urls.py`, `views.py`, `tests/test_notifications.py`

`NotificationListView` and the `list` route. Tests: signed out redirects to sign-in; lists only the person's own, newest first; read and unread told apart by the row's unread mark; 20 a page and page 2 holds the rest; no notifications draws the empty state.

- [ ] T003 [US2] Opening one, and marking all read

**Files**: `views.py`, `urls.py`, `tests/test_notifications.py`

`OpenNotificationView` and `MarkAllReadView`. Tests: opening marks read and redirects to its url; another person's is 404; with no url it redirects to the list; mark all read by POST leaves none unread and redirects; GET is refused.

- [ ] T004 [US2] The bell's count

**Files**: `mvp_community/templatetags/__init__.py`, `mvp_community/templatetags/mvp_community_notifications.py`, `mvp_community/templates/cotton/mvp_community/notifications/bell.html`, `tests/test_bell.py`

The tag and the bell's switch from the context variable to it. Tests: the shell shows the count; none unread shows no count; signed out shows no bell; a notification only on another channel is not counted.

- [ ] T005 [US2] The bell refreshes

**Files**: `views.py`, `urls.py`, `mvp_community/templates/mvp_community/notifications/bell_partial.html`, `demo/views.py`, `demo/urls.py`, `demo/templates/demo/overview.html`, `tests/test_bell.py`

`BellView`, the `bell` route, and the demo's "Send me a notification". Tests: the bell route returns the bell with the current count; the bell carries the `hx-get` to that route and the `notifications:changed` trigger; signed out is redirected.

---

## Phase 2: User Story 3 — A person chooses which notifications they receive (P2)

Issue: #11. Delivers FR-010, FR-011, FR-013.

### Group 1

- [ ] T006 [US3] The preferences page

**Files**: `views.py`, `urls.py`, `tests/test_preferences.py`

`PreferencesView` GET and the `preferences` route at `account-center/notifications/`. Tests: signed out redirects; every registered type is listed against every channel with the person's current choice; a required choice is drawn on and disabled; with no types registered the empty state is drawn.

- [ ] T007 [US3] Saving preferences

**Files**: `views.py`, `tests/test_preferences.py`

POST. Tests: a type turned off on the site and saved is shown off on the next visit and every other choice is unchanged; a notification of that type sent afterwards does not reach the notifications page or the count; one already received stays listed; saving adds a success message and redirects to the page.

---

## Phase 3: User Story 1 — A developer turns notifications on (P1)

Issue: #9. Delivers FR-001, FR-002, FR-009, FR-012, FR-014.

### Group 1

- [ ] T008 [US1] The Account Center entry and card

**Files**: `mvp_community/apps.py`, `mvp_community/integrations/notifications/menus.py`, `tests/test_account_center.py`

`ready()` imports the menus module when `generic_notifications` is installed. Tests: the Account Center menu has the entry, linking to preferences; the landing page has the card linking to preferences; the preferences page marks the Account Center sidebar current.

- [ ] T009 [US1] Any template can be replaced

**Files**: `tests/templates/…`, `tests/test_overrides.py`

Tests: a project template of the same name as the notification row component, and one for the preferences page, each replaces the package's and leaves the rest of the feature drawn as before.

- [ ] T010 [US1] The base install

**Files**: `tests/test_smoke.py` only if the existing test does not already cover the tag library

Confirm the existing base-install test imports `mvp_community.templatetags.mvp_community_notifications` with the extra blocked. Add nothing if it does. Test only if it does not.

- [ ] T011 [US1] Documentation

**Files**: `docs/notifications.md`, `README.md`, `docs/index` if one exists

As plan, *Documentation*. Every setting and name it quotes must match the branch.
