# Implementation Plan — 005 Notifications by web push

**Branch**: `005-notifications-by-web-push` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

Push becomes a fifth extra, `push`, built on django-push-notifications' `WebPushDevice` and reached
through a channel registered with django-generic-notifications. Its code lives in a new integration
module, `mvp_community.integrations.push`: the channel, the views that store and stop a
subscription and serve the service worker, a system check and a small helper module. The push card
approved in the sketch is kept as it is drawn, its stand-in data replaced by the real
subscriptions and its state chosen in the browser by a script in the component.

## Technical Context

- Python 3.12+, Django 5.2 to 6.1, django-mvp, daisy-cotton components, Alpine (on every django-mvp
  page).
- New dependencies, in the `push` extra only: `django-push-notifications[wp]>=3.3` (brings
  pywebpush and py-vapid) and `ua-parser>=1.0`. The extra also names
  `django-generic-notifications>=2.4`.
- No models and no migrations of the package's own. django-push-notifications brings its own
  migrations.
- Push needs a secure context in the browser: HTTPS, or `localhost`.

## Constitution Check

- **Article II, III (simplicity, anti-abstraction)**: one channel class, three views, one check,
  two small helpers. No base classes, registries or settings of the package's own.
- **Article V (security)**: the subscribe and stop views require a signed-in person and CSRF,
  touch only that person's rows, and validate the posted subscription. The private key stays in
  the project's settings.
- **Article VI (documentation)**: a new page, `docs/developer/push.md`, linked from the README and
  from the notifications page.
- **Article VII (dependencies)**: the two packages are justified in research.md, and isolated in
  their own extra so G2 holds.
- **Article VIII (i18n)**: every string on the card, in the views' messages and in a push is
  translatable.
- **Article XII (scope)**: web push only, no native push, no real-time delivery.
- **Article XIII (extras)**: a new extra with its own integration module. Nothing outside
  `mvp_community.integrations.push` imports `push_notifications`, `pywebpush`, `py_vapid` or
  `ua_parser`. The notifications integration reaches the push module only when the push channel
  is registered.
- **Article XIV (templates first)**: the card, the script and the service worker are templates a
  project overrides by name.

## Design

### The extra (`pyproject.toml`)

```toml
push = [
    "django-generic-notifications>=2.4",
    "django-push-notifications[wp]>=3.3",
    "ua-parser>=1.0",
]
```

The development dependency group installs `push` with the other extras. The base-install test in
`tests/test_smoke.py` already blocks every extra's import names, read from the package metadata,
so it covers the new packages with no change.

### Set-up (`integrations/push/setup.py`, `mvp_community/apps.py`)

`configure()` registers `PushChannel` with django-generic-notifications, forced, as the
notifications set-up does. `MvpCommunityConfig.ready` calls it when both `generic_notifications`
and `push_notifications` are installed, after the notifications set-up, and imports the push
checks. Without `push_notifications` nothing registers and the page is unchanged (FR-002).

### The channel (`integrations/push/channels.py`)

```python
class PushChannel(BaseChannel):
    key = "push"
    name = _("Push")
    supports_realtime = True
    supports_digest = False
```

- `recipient_language(user)` returns `settings.LANGUAGE_CODE`, as the email channel's does.
- `payload(notification)` returns the JSON string: `title` from `get_subject()`, `body` from
  `get_text()` cut with `Truncator(...).chars(400)`, `url` the path of
  `mvp_community_notifications:open` for the notification. Built inside
  `translation.override(self.recipient_language(...))`.
- `send_now(notification)` sends the payload to each of the recipient's active `WebPushDevice`
  rows with `device.send_message(payload)`. A `WebPushError` from one device is logged at warning
  and the loop goes on (FR-007); a gone subscription is already retired by the library (FR-014).
- `send_test(device)` sends one push whose title is the site's name from django-mvp's config if
  available, else `_("Push notifications")`, whose body is `_("Push is on for this browser.")`,
  and whose url is the preferences page's path. Errors are logged, never raised.

### The key and the browser name (`integrations/push/subscriptions.py`)

- `application_server_key()` returns the URL-safe base64 of the raw public key derived from
  `PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"]` with py-vapid: `Vapid01.from_file` when the value
  is a path to an existing file, `Vapid01.from_string` otherwise. Cached per process with
  `functools.cache`.
- `browser_name(user_agent)` → "Chrome on Android" (research.md, *Naming a browser*).
- `device_kind(name)` → `"phone"`, `"tablet"` or `"computer"`.
- `browser_type(user_agent)` → the `WebPushDevice.browser` choice for the family (Chrome, Firefox,
  Opera, Edge, Safari), Chrome when none matches. The full endpoint is stored, so the field is
  bookkeeping only.
- `card_context(request)` → the dict the push card renders: `subscriptions` (active, newest first,
  each the device with `kind` attached), `just_turned_on` (popped from the session),
  `application_server_key`, and the URLs of the worker and the subscribe view.

### The views (`integrations/push/views.py`, `integrations/push/urls.py`)

`app_name = "mvp_community_push"`, included at the root like the notifications URLs:

| Name | Path | View |
|---|---|---|
| `worker` | `notifications/push/worker.js` | `WorkerView`: renders `mvp_community/push/worker.js` with `content_type="text/javascript"`, `login_not_required`, never cached by the browser beyond revalidation (`Cache-Control: no-cache`). |
| `subscribe` | `notifications/push/subscribe/` | `SubscribeView`: POST only, `LoginRequiredMixin` with `raise_exception`. Reads JSON `{"endpoint", "keys": {"p256dh", "auth"}}`. The endpoint must be an `https://` URL; `p256dh` at most 88 and `auth` at most 24 characters, both present. Bad JSON or a bad field → 400 with nothing stored. Otherwise `update_or_create(user=…, registration_id=endpoint, defaults={p256dh, auth, active: True, name, browser})`, sets `request.session["mvp_community_push_turned_on"] = True`, sends the test push, and answers 204. |
| `stop` | `notifications/push/<int:pk>/stop/` | `StopView`: POST only, signed-in. `get_object_or_404(WebPushDevice, pk=pk, user=request.user)`, deletes it, adds `messages.success(_("Push to {name} is stopped."))`, redirects to the preferences page. Another person's id is a 404 and changes nothing (FR-013). |

### The preferences page

`PreferencesView.get_context_data` adds `push` when the registry holds a channel keyed `push`:
it imports `card_context` from the push integration inside that branch, so the notifications
extra never imports the push packages. The template keeps the sketch's call:
`{% if push %}<c-mvp_community.notifications.push_card :push="push" />{% endif %}` above the grid.

### The push card (`cotton/mvp_community/notifications/push_card.html`)

The markup, copy and order Sam approved are kept. What changes:

- Every state block is rendered, each shown by Alpine for one state:
  `x-data="mvpCommunityPush"` on the card's body, `x-show="state === 'offer'"` and so on, all
  `x-cloak` but the no-script note. Before the script has decided, no state is shown.
- The rows come from the real subscriptions. Each row carries `data-endpoint` with its
  `registration_id`. "This browser · " is wrapped in a span shown when that row's endpoint is the
  browser's own.
- The turn-on control is a plain button: its click calls `turnOn()`.
- Each Stop form posts to `mvp_community_push:stop`. For the browser's own row, the submit
  handler unsubscribes in the browser first.
- A small inline script, written once, registers `Alpine.data("mvpCommunityPush", …)` on
  `alpine:init`. It reads the key and the two URLs from `data-` attributes on the card. It holds
  `state`, `asking` and `endpoint`; `init()` registers the worker (when supported) and picks the
  state as research.md lists; `turnOn()` asks permission inside the click, subscribes, posts the
  JSON with the CSRF token, and reloads; a refusal moves to `denied`.
- The `just_turned_on` alert shows in the `on` state only when the flag was set.

### The service worker (`templates/mvp_community/push/worker.js`)

Two listeners. `push`: parse the JSON, `showNotification(title, {body, data: {url}})` inside
`event.waitUntil`. `notificationclick`: close it, then focus an open window on that URL or
`clients.openWindow(new URL(url, self.location.origin))`.

### System check (`integrations/push/checks.py`)

`mvp_community.E002`, registered when the push extra is configured: `PUSH_NOTIFICATIONS_SETTINGS`
lacks `WP_PRIVATE_KEY` or `WP_CLAIMS` (or `WP_CLAIMS` has no `sub`). One error per missing setting,
naming it, with a hint pointing at the documentation (FR-003).

### The demo

- `INSTALLED_APPS` gains `push_notifications`; the URLs include the push URLs.
- `PUSH_NOTIFICATIONS_SETTINGS` points `WP_PRIVATE_KEY` at `.vapid_private.pem` in the project
  root, generated with py-vapid on first start when it does not exist, and ignored by git.
  `WP_CLAIMS = {"sub": "mailto:admin@example.com"}`.
- The icons the card names stay in `MVP_CONFIG`.
- The sketch's stand-ins are deleted: `demo/sketch_push.py`, its context processor entry, its two
  URLs, its import in `demo/apps.py`.
- `seed_push` (development only, refuses without DEBUG like `seed_demo`) gives `regular.user` two
  subscriptions that look like a phone and a computer, so the list can be walked on a page served
  over plain HTTP, where the browser itself cannot subscribe.
- The existing test fixture `without_mail` (`test_views.py`) keeps only the website channel, so
  it also removes `push`. That is the one pre-existing test this feature edits (decisions D13).

### Tests

`tests/test_integrations/test_push/`, one class per subject:

1. `TestSetup`: with the push app installed, `push` is a registered channel; `configure()` twice
   leaves one.
2. `TestPreferencesWithoutPush`: with the push channel removed from the registry, the page has no
   push card and no push column (FR-002).
3. `TestChecks`: E002 for a missing private key, missing claims, claims with no `sub`; nothing
   when both are set.
4. `TestPushChannel`: a notification for a person with two active devices sends one payload to
   each (patch `WebPushDevice.send_message`); an inactive device and another person's device get
   none; the payload's url is the open view's path; the title and body come from the
   notification; a person with push off for the type gets nothing (through
   `send_notification`); a device raising `WebPushError` does not stop the next device and does not
   raise; the payload is written in the language `recipient_language` returns.
5. `TestSubscriptions`: `browser_name` for an iPhone Safari, an Android Chrome, a Windows Firefox,
   an empty string; `device_kind` for each; `application_server_key` returns 65 bytes when
   decoded, from a key file and from a key string.
6. `TestSubscribeView`: a signed-out POST is refused and stores nothing; a valid POST stores one
   active device for the person with its name and sends one test push; posting the same endpoint
   again leaves one; the same endpoint from another person stores a second row for them; a
   non-https endpoint, missing keys and malformed JSON are 400 with nothing stored; GET is 405;
   the next preferences page shows the turned-on alert once.
7. `TestStopView`: the person's own device is deleted and a message names it; another person's is
   a 404 and is kept; signed out changes nothing.
8. `TestPushCard`: the preferences page lists the person's active devices newest first, with
   their names and the right icon names, and none of an inactive or another person's; no list
   when there are none; each row's stop form posts to that device's stop URL; the card carries
   the public key and the two URLs; the no-script note is present.
9. `TestWorkerView`: served signed out, JavaScript content type, from the template a project can
   override (tests' override directory).

Nothing tests wording or appearance. The script and the worker are exercised in a real browser
at the walkthrough; no Python test reads JavaScript source.

### Documentation

- `docs/developer/push.md`: installing the extra, generating the key pair (`vapid --gen`), the two
  settings, the URLs, naming `PushChannel` in a type's channels, the icon names the card uses,
  HTTPS, what replacing the key pair does, what iPhone and iPad need (Home Screen), a project with
  its own service worker, overriding the card, the worker and `recipient_language`, the system
  check.
- `README.md`: the extra in the install list and a link to the page.
- `CONTEXT.md`: `push` added to **Extra**.
- `docs/developer/notifications.md`: push named among the channels, linking the new page.
- `CHANGELOG.md` entry if the repo keeps one.

### Story order

US1 (developer, channel and set-up) → US2 (turning push on) → US3 (the list and stopping).
