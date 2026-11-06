# Tasks — 004 Notifications by email, and digests

**Branch**: `004-notifications-by-email` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md) · **Sketch**: [sketch.md](sketch.md)

Groups run one after another, never in parallel. Every task with behaviour follows the red-green-refactor cycle of Article I. A task is done when its tests pass, the tree is green and the work is committed. The templates approved in the sketch are kept. The Python the sketch wrote is replaced, test-first.

## Order

US1 → US2 → US3.

---

## Phase 1: User Story 1 — A developer sends notifications by email (P1)

Issue: #25. Delivers FR-001 to FR-004, FR-006 to FR-008, FR-013 to FR-015, FR-016, FR-017.

### Group 1

- [ ] T001 [US1] The extra's set-up: weekly digest, System Message removed, email channel swapped or removed

**Files**: `mvp_community/integrations/notifications/__init__.py`, `mvp_community/integrations/notifications/setup.py`, `mvp_community/integrations/notifications/checks.py`, `mvp_community/integrations/notifications/frequencies.py`, `mvp_community/integrations/notifications/channels.py`, `mvp_community/integrations/notifications/views.py`, `mvp_community/apps.py`, `demo/notifications.py`, `tests/test_integrations/test_notifications/test_setup.py`, `tests/test_integrations/test_notifications/test_views.py`

Plan, *Set-up*, with an empty `NotificationEmailChannel` subclass, the system check, and the view's empty `frequencies` without an email channel. Tests 1, 1a and 2 of plan, *Tests*.

- [ ] T002 [US1] The channel: language, template context, always-sent types at once

**Files**: `mvp_community/integrations/notifications/channels.py`, `tests/test_integrations/test_notifications/test_channels.py`

Plan, *The channel*, without the unsubscribe address. Tests 3, 4, 6, 7 and 8.

### Group 2

- [ ] T003 [US1] Digests through the channel, and the email templates read their context

**Files**: `mvp_community/integrations/notifications/channels.py`, `mvp_community/templates/notifications/email/**`, `mvp_community/templatetags/mvp_community_notifications.py`, `tests/test_integrations/test_notifications/test_channels.py`

Test 5. `notification_type_name` rebuilt on the registry's `get_type`.

- [ ] T004 [US1] The demo: security notices by email, the site domain, the email seed through the real path

**Files**: `demo/notifications.py`, `demo/management/commands/seed_demo.py`, `demo/management/commands/seed_notification_email.py`, `tests/test_demo.py`

Plan, *The demo*.

- [ ] T005 [US1] Documentation: install, what the library adds, digests, language, template names

**Files**: `docs/developer/notifications.md`, `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`

Sections 1, 2, 3, 5 and 6 of plan, *Documentation*, and R4's brief.

---

## Phase 2: User Story 2 — A person chooses how often notification email comes (P1)

Issue: #26. Delivers FR-005, FR-006, FR-007, FR-016.

- [ ] T006 [US2] The preferences page's frequency choice

**Files**: `mvp_community/integrations/notifications/views.py`, `mvp_community/templates/mvp_community/notifications/preferences.html`, `tests/test_integrations/test_notifications/test_views.py`

Plan, *The preferences page*. Tests 9 and 10.

- [ ] T007 [US2] Documentation: the frequency choice

**Files**: `docs/developer/notifications.md`

Section 7 of plan, *Documentation*, and the preferences page's description.

---

## Phase 3: User Story 3 — A person unsubscribes from notification email in one click (P2)

Issue: #27. Delivers FR-009 to FR-013.

### Group 1

- [ ] T008 [US3] The unsubscribe address

**Files**: `mvp_community/integrations/notifications/unsubscribe.py`, `tests/test_integrations/test_notifications/test_unsubscribe.py`

Plan, *The unsubscribe address*. Tests 11 and 12.

- [ ] T009 [US3] The unsubscribe page and the one-click request

**Files**: `mvp_community/integrations/notifications/views.py`, `mvp_community/integrations/notifications/urls.py`, `mvp_community/templates/mvp_community/notifications/unsubscribe.html`, `tests/test_integrations/test_notifications/test_views.py`

Plan, *The unsubscribe view*. Tests 13, 14, 16, 17 and 18.

### Group 2

- [ ] T010 [US3] The address and the headers on every email

**Files**: `mvp_community/integrations/notifications/channels.py`, `mvp_community/templates/notifications/email/**`, `mvp_community/templatetags/mvp_community_notifications.py`, `tests/test_integrations/test_notifications/test_channels.py`

Test 15. The sketch's `notification_unsubscribe_token` tag becomes `notification_unsubscribe_url`, built on `UnsubscribeLink`.

- [ ] T011 [US3] Documentation: unsubscribing, and the glossary

**Files**: `docs/developer/notifications.md`, `CONTEXT.md`, `CHANGELOG.md`

Section 4 of plan, *Documentation*, and *Unsubscribe link* in `CONTEXT.md`.
