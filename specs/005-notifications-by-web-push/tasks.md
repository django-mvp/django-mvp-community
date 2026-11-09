# Tasks — 005 Notifications by web push

**Branch**: `005-notifications-by-web-push` · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md) · **Spec**: [spec.md](spec.md) · **Sketch**: [sketch.md](sketch.md)

Groups run one after another, never in parallel. Every task with behaviour follows the red-green-refactor cycle of Article I. A task is done when its tests pass, the tree is green and the work is committed. The push card's markup, copy and order approved in the sketch are kept. The Python the sketch wrote is deleted and replaced, test-first.

## Order

US1 → US2 → US3.

---

## Phase 1: User Story 1 — A developer sends notifications by push (P1)

Issue: #30. Delivers FR-001 to FR-007, FR-017 to FR-019.

### Group 1

- [ ] T001 [US1] The `push` extra, the integration module's set-up and the demo's push configuration

**Files**: `pyproject.toml`, `uv.lock`, `mvp_community/apps.py`, `mvp_community/integrations/push/__init__.py`, `mvp_community/integrations/push/setup.py`, `mvp_community/integrations/push/channels.py`, `mvp_community/integrations/push/checks.py`, `demo/settings.py`, `demo/urls.py`, `demo/apps.py`, `demo/sketch_push.py` (deleted), `.gitignore`, `tests/test_integrations/test_push/__init__.py`, `tests/test_integrations/test_push/test_setup.py`, `tests/test_integrations/test_push/test_checks.py`, `tests/test_apps.py` (one new test), `tests/test_integrations/test_notifications/test_views.py` (fixture `without_mail` only)

Plan, *The extra*, *Set-up*, *System check*, *The demo* (without `seed_push`, the key generated in memory). `PushChannel` with its class attributes and an empty `send_now`. Tests 1 and 3. The sketch's stand-ins are removed in this task.

- [ ] T002 [US1] The channel sends each notification to every active subscription of its recipient

**Files**: `mvp_community/integrations/push/channels.py`, `tests/test_integrations/test_push/test_channels.py`

Plan, *The channel*, `recipient_language`, `payload` and `send_now`. Test 4.

### Group 2

- [ ] T003 [US1] The preferences page shows push only when it is set up

**Files**: `mvp_community/integrations/notifications/views.py`, `mvp_community/integrations/push/subscriptions.py`, `mvp_community/templates/mvp_community/notifications/preferences.html`, `tests/test_integrations/test_push/test_subscriptions.py`

Plan, *The preferences page*, with `card_context` returning the active subscriptions and the two URLs only; the public key is added in T005 and each row's `Browser` in T009. Test 2. The card renders from real context; the stand-in URLs are gone from the template.

- [ ] T004 [US1] The developer documentation for push

**Files**: `docs/developer/push.md`, `docs/developer/notifications.md`, `README.md`, `CONTEXT.md`

Plan, *Documentation*. Every example runs against the branch.

---

## Phase 2: User Story 2 — A person turns push on for the browser they are using (P1)

Issue: #31. Delivers FR-008 to FR-011, FR-016, FR-017, FR-019.

### Group 3

- [ ] T005 [US2] The public key, the browser read from a user agent, and the accepted push services

**Files**: `mvp_community/integrations/push/subscriptions.py`, `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`, `tests/test_integrations/test_push/test_subscriptions.py`

Plan, *The key, the browser and the card's context*: `application_server_key` (added to `card_context` and to the card's data attributes), `Browser`, `is_push_endpoint`. Test 5.

- [ ] T006 [US2] The subscribe view stores one subscription per person and browser and sends a test push

**Files**: `mvp_community/integrations/push/views.py`, `mvp_community/integrations/push/urls.py`, `mvp_community/integrations/push/channels.py`, `mvp_community/integrations/push/subscriptions.py`, `tests/test_integrations/test_push/test_views.py`

Plan, *The views*, `subscribe`, and the channel's `send_test`. Test 6.

- [ ] T007 [US2] The service worker shows a push and opens the notification

**Files**: `mvp_community/integrations/push/views.py`, `mvp_community/integrations/push/urls.py`, `mvp_community/templates/mvp_community/push/worker.js`, `tests/test_integrations/test_push/test_views.py`, `tests/templates/overrides/**`

Plan, *The views*, `worker`, and *The service worker*. Test 9.

- [ ] T008 [US2] The push card picks its state in the browser and turns push on

**Files**: `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`, `tests/test_integrations/test_push/test_subscriptions.py`

Plan, *The push card*, every state block, the script and the `@prop` header. The card's data attributes, the `<noscript>` element and a project's override of the component are tested (test 8, those parts); the script is checked in a browser at the walkthrough.

---

## Phase 3: User Story 3 — A person sees and stops their push subscriptions (P2)

Issue: #32. Delivers FR-012 to FR-015, FR-017, FR-019.

### Group 4

- [ ] T009 [US3] The list of the person's browsers receiving push

**Files**: `mvp_community/integrations/push/subscriptions.py`, `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`, `tests/test_integrations/test_push/test_subscriptions.py`

Plan, *The push card*, the rows, each with the `Browser` read from its stored user agent. Test 8, the list.

- [ ] T010 [US3] Stopping push to one browser

**Files**: `mvp_community/integrations/push/views.py`, `mvp_community/integrations/push/urls.py`, `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`, `tests/test_integrations/test_push/test_views.py`

Plan, *The views*, `stop`, and the row's form, with no script. Test 7.

- [ ] T011 [US3] The demo seeds push subscriptions to walk the list, and the message catalogue is regenerated

**Files**: `demo/management/commands/seed_push.py`, `tests/test_demo.py`, `mvp_community/locale/en/LC_MESSAGES/django.po`

Plan, *The demo*, `seed_push`, following `seed_demo`'s refusal without DEBUG, and *Documentation*, the catalogue.

---

## Convergence

- [ ] T012 [US2] Name the subscribe view's result without a leading underscore

**Files**: `mvp_community/integrations/push/views.py`

Found at convergence: the unused second value of `update_or_create` was bound to a name with a leading underscore, which the repo's standards rule out.

- [ ] T013 [US2] Wait for the push card's own worker, not for a worker controlling the page

**Files**: `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`

Found in the browser check: the script waited on `navigator.serviceWorker.ready`, which resolves only for a worker whose scope covers the page. The push worker's scope is below the preferences page, so the card never chose a state. The script now waits for its own registration's worker to activate, and logs a failure to turn push on to the console.

## Review fixes

- [ ] T014 [US2] Accept only plain push-service endpoints and well-formed keys

**Files**: `mvp_community/integrations/push/subscriptions.py`, `mvp_community/integrations/push/views.py`, `tests/test_integrations/test_push/test_subscriptions.py`, `tests/test_integrations/test_push/test_views.py`, `tests/factories.py`

A backslash in the host passed the endpoint check while the HTTP client connected elsewhere. Endpoints are now refused unless their host is a plain DNS name, the URL holds only printable ASCII without a backslash, and it is at most 1024 characters. The `p256dh` key must decode to 65 bytes and the `auth` secret to 16.

- [ ] T015 [US2] Turning push on again after the site's key was replaced

**Files**: `mvp_community/templates/cotton/mvp_community/notifications/push_card.html`, `mvp_community/integrations/push/views.py`, `docs/developer/push.md`, `tests/test_integrations/test_push/test_views.py`

A browser subscription made with an earlier key counts as none: the card offers push, and turning it on unsubscribes the old one, subscribes with the current key and sends the old endpoint as `previous`, whose row the view deletes for that person.

- [ ] T016 [US2] A browser test that the push card chooses a state

**Files**: `tests/test_integrations/test_push/test_subscriptions.py`

Guards T013: on the live server the card reaches the offer state; with the old wait on `serviceWorker.ready` it never does.

- [ ] T017 [US1] Smaller review points

**Files**: `mvp_community/integrations/push/views.py`, `docs/developer/push.md`, `demo/settings.py`, `tests/factories.py`, `tests/test_integrations/test_push/test_channels.py`, `tests/test_integrations/test_push/test_subscriptions.py`, `tests/test_integrations/test_push/test_views.py`

The test push goes through the registered push channel, so a project's subclass applies; the guide shows the URL include; the demo's key variable has no leading underscore; push subscriptions in the tests come from one factory; the empty-list test fails when the guard is removed.

- [ ] T018 [US2] Keep at most 20 push subscriptions per person

**Files**: `mvp_community/integrations/push/views.py`, `docs/developer/push.md`, `tests/test_integrations/test_push/test_views.py`

Closes the review's open medium: storing a subscription deletes the person's oldest beyond `SUBSCRIPTION_LIMIT`, since every notification is sent to each one.

## Merge-gate fixes

- [ ] T019 [US1] Every push carries an icon

**Files**: `mvp_community/integrations/push/channels.py`, `mvp_community/templates/mvp_community/push/worker.js`, `demo/settings.py`, `demo/static/demo/push-icon.png`, `docs/developer/push.md`, `tests/test_integrations/test_push/test_channels.py`, `tests/test_integrations/test_push/test_views.py`, `specs/005-notifications-by-web-push/spec.md`, `specs/005-notifications-by-web-push/decisions.md`

Asked for at the merge gate. The payload carries the type's `push_icon`, else `MVP_COMMUNITY_PUSH_ICON`, else the site's brand icon, as an absolute address; the worker shows it.
