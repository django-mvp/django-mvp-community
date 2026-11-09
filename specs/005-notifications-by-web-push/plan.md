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
  rows with `subscription.send_message(payload)`. A `WebPushError` or a
  `requests.RequestException` (a timeout or refused connection, which the library does not wrap)
  from one subscription is logged at warning and the loop goes on (FR-004, FR-007); a gone
  subscription is already retired by the library (FR-014).
- `send_test(subscription)` sends one push titled `_("Push notifications")`, with the body
  `_("Push is on for this browser.")` and the preferences page's path as its url. The same two
  errors are logged, never raised, so turning push on never fails on a slow push service.

### The key, the browser and the card's context (`integrations/push/subscriptions.py`)

- `application_server_key()` returns the URL-safe base64 of the raw public key derived from
  `PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"]` with py-vapid: `Vapid01.from_file` when the value
  is a path to an existing file, `Vapid01.from_string` otherwise. Not cached: it runs once per
  preferences page.
- `Browser`, a frozen dataclass built from a user agent string with `Browser.from_user_agent(ua)`
  (ua-parser). Properties: `family` ("Chrome", "Safari", leading "Mobile " dropped, "" when
  unreadable), `place` (the device family for an iPhone or iPad, the operating system otherwise),
  `kind` (`"phone"` for iPhone and Android, `"tablet"` for iPad, `"computer"` otherwise) and
  `label`, the translatable `"{family} on {place}"`, or `_("Unknown browser")` when unreadable.
- The subscription stores the request's user agent in `WebPushDevice.name`, cut to 255 characters.
  The name shown, and its icon, are read from it when the page is drawn, so they are translated for
  the reader (FR-019). `WebPushDevice.browser` keeps the library's default: the library reads it
  only for an endpoint that is not a full `https://` URL, which this package never stores.
- `ALLOWED_PUSH_HOSTS` and `is_push_endpoint(url)`: an endpoint is accepted only when it is an
  `https://` URL on a push service the major browsers use: `fcm.googleapis.com`,
  `updates.push.services.mozilla.com`, `web.push.apple.com`, a host ending in
  `.notify.windows.com`, or a host ending in `.push.apple.com`. Anything else is refused, so a
  signed-in person cannot make the server post to an address of their choosing.
- `card_context(request)` → the dict the push card renders: `subscriptions` (active, newest first,
  each paired with its `Browser`), `just_turned_on` (popped from the session),
  `application_server_key`, and the URLs of the worker and the subscribe view.

### The views (`integrations/push/views.py`, `integrations/push/urls.py`)

`app_name = "mvp_community_push"`, included at the root like the notifications URLs:

| Name | Path | View |
|---|---|---|
| `worker` | `notifications/push/worker.js` | `WorkerView`: renders `mvp_community/push/worker.js` with `content_type="text/javascript"`, `login_not_required`, never cached by the browser beyond revalidation (`Cache-Control: no-cache`). |
| `subscribe` | `notifications/push/subscribe/` | `SubscribeView`: POST only, `LoginRequiredMixin` with `raise_exception`. Reads JSON `{"endpoint", "keys": {"p256dh", "auth"}}`. The endpoint must pass `is_push_endpoint`; `p256dh` at most 88 and `auth` at most 24 characters, both present. Bad JSON or a bad field → 400 with nothing stored. Otherwise `update_or_create(user=…, registration_id=endpoint, defaults={p256dh, auth, active: True, name: user agent})`, sets `request.session["mvp_community_push_turned_on"] = True`, sends the test push, and answers 204. |
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
- Each Stop form posts to `mvp_community_push:stop`, with no script. The browser's own
  subscription is left alone, because a browser shared by two people has one endpoint for both.
  After stopping it the page offers to turn push on again, since the server no longer lists that
  endpoint.
- A small inline script, written once, registers `Alpine.data("mvpCommunityPush", …)` on
  `alpine:init`. It reads the key and the two URLs from `data-` attributes on the card. It holds
  `state`, `asking` and `endpoint`; `init()` registers the worker (when supported) and picks the
  state as research.md lists; `turnOn()` asks permission inside the click, subscribes (or reuses the existing
  subscription), posts the JSON with the CSRF token read from a rendered `{% csrf_token %}` input,
  and reloads; a refusal moves to `denied`.
- The component's `@prop` header describes the real context.
- The `just_turned_on` alert shows in the `on` state only when the flag was set.

### The service worker (`templates/mvp_community/push/worker.js`)

Two listeners. `push`: parse the JSON, `showNotification(title, {body, data: {url}})` inside
`event.waitUntil`. `notificationclick`: close it, then `clients.openWindow(new URL(url, self.location.origin))`
inside `event.waitUntil`.

### System check (`integrations/push/checks.py`)

`mvp_community.E002`, registered when the push extra is configured: `WP_PRIVATE_KEY` or `WP_CLAIMS`
is empty in `push_notifications.settings.PUSH_NOTIFICATIONS_SETTINGS` (or `WP_CLAIMS` has no
`sub`). The check reads the library's dict, not Django's setting, and tests for an empty value,
because the library fills both keys with `None` when it loads. One error per missing setting,
naming it, with a hint pointing at the documentation (FR-003).

### The demo

- `INSTALLED_APPS` gains `push_notifications`; the URLs include the push URLs.
- `PUSH_NOTIFICATIONS_SETTINGS` sets `WP_PRIVATE_KEY` to a development-only key generated by
  py-vapid when `demo/settings.py` is imported and kept in memory for the process. Nothing is
  written to disk, so the test settings that import it leave no file behind. A restart gives a new
  key, which retires the demo's earlier subscriptions; the demo says so in a comment.
  `WP_CLAIMS = {"sub": "mailto:admin@example.com"}`.
- The icons the card names stay in `EASY_ICONS`.
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
   leaves one. In `tests/test_apps.py`, following its existing pattern, the app's `ready()` with
   `push_notifications` not installed registers no push channel (FR-002).
2. `TestPreferencesWithoutPush`: with the push channel removed from the registry, the page has no
   push card and no push column (FR-002).
3. `TestChecks`: E002 for a private key that is absent and one that is `None`, the same for the
   claims, and claims with no `sub`; nothing when both are set. Each test patches the library's
   dict (`push_notifications.settings.PUSH_NOTIFICATIONS_SETTINGS`), so the absent and `None`
   cases are both real.
4. `TestPushChannel`: a notification for a person with two active devices sends one payload to
   each (patch `WebPushDevice.send_message`); an inactive device and another person's device get
   none; the payload's url is the open view's path; the title and body come from the
   notification; a person with push off for the type gets nothing (through
   `send_notification`); a subscription raising `WebPushError`, and one raising `requests.Timeout`, does
   not stop the next and does not raise; the payload is written in the language
   `recipient_language` returns; a type the person set to a daily digest is still pushed at once
   (FR-005).
5. `TestBrowser` and `TestApplicationServerKey`: `Browser.from_user_agent` for an iPhone Safari,
   an Android Chrome, a Windows Firefox, an iPad and an empty string, asserting `family`, `place`
   and `kind`, and `label` falling back for the empty one; `application_server_key` returns 65
   bytes when decoded, from a key file and from a key string, and two different keys give two
   different results. `TestPushEndpoint`: each allowed host is accepted, and `http://`, an
   unlisted host, a host that only contains an allowed one (`fcm.googleapis.com.example.org`) and
   a non-URL are refused.
6. `TestSubscribeView`: a signed-out POST is refused and stores nothing; a valid POST stores one
   active device for the person with its name and sends one test push; posting the same endpoint
   again leaves one; the same endpoint from another person stores a second row for them; an
   endpoint `is_push_endpoint` refuses, missing keys and malformed JSON are 400 with nothing
   stored; a test push that times out still answers 204 and stores the subscription; GET is 405;
   the next preferences page shows the turned-on alert once.
7. `TestStopView`: the person's own device is deleted and a message names it; another person's is
   a 404 and is kept; signed out changes nothing.
8. `TestPushCard`: the preferences page lists the person's active subscriptions newest first,
   each with the `Browser` read from its stored user agent and its icon name, and none of an inactive or another person's; no list
   when there are none; each row's stop form posts to that device's stop URL; the card carries
   the public key and the two URLs; a `<noscript>` element is present (never its copy); a project's override of the
   component (tests' override directory) replaces it (US1 scenario 9).
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
- `docs/developer/push.md` says that production servers do not run system checks, so a missing key
  shows first as an error on the preferences page; `manage.py check --deploy` reports it.
- The English message catalogue in `mvp_community/locale/en/` is regenerated with the new strings.

### Story order

US1 (developer, channel and set-up) → US2 (turning push on) → US3 (the list and stopping).
