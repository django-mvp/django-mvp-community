# Research: Notifications by web push

## Assumptions checked

- **django-push-notifications runs on the Django versions this package supports.** Its package
  metadata lists Django up to 4.0 only, but its latest release (3.3.0, 2025-11) installs with its
  web push extra on Django 6.1.3, migrates, and reports no missing migrations under
  `makemigrations --check`. Confirmed.
- **It stores what a push subscription needs.** `WebPushDevice` has `user`, `name` (255
  characters, optional), `active`, `date_created`, `registration_id`, `p256dh`, `auth` and
  `browser`. Confirmed.
- **It retires a subscription the push service reports as gone.** `webpush_send_message` sets
  `active = False` and saves on a 404 or 410 from the push service, and raises `WebPushError` on
  any other refusal (`push_notifications/webpush.py`). Confirmed by reading the installed source.
- **Deleting an account removes its subscriptions.** `Device.user` is a foreign key with
  `on_delete=CASCADE` (`push_notifications/models.py`). FR-015 is the library's behaviour and gets
  no test here.
- **A new channel appears on the preferences page by itself.** `PreferencesView` passes
  `registry.get_all_channels()` to the template, which draws a column per channel. Confirmed in
  the sketch, where a stand-in push channel drew its column with no change to the view.
- **One channel failing does not stop the others.** django-generic-notifications calls each
  channel's `process` inside its own `try` (`generic_notifications/__init__.py`, `send_notification`),
  so a push that raises still leaves the site and email delivered.
- **Storing a subscription from the browser.** django-push-notifications' own endpoint is built on
  Django REST framework, which this package does not depend on. A view of this package's stores
  it instead.

## The sketch's requirements, and how each is met

| Need (sketch.md) | Met by |
|---|---|
| Whether push is set up | The push channel is registered only when `push_notifications` is installed. The preferences view adds the push card's context when the registry holds a channel keyed `push`, as it offers frequencies only when `email` is registered. |
| The person's active subscriptions, newest first, with a readable name, a device kind and a date | `WebPushDevice.objects.filter(user=…, active=True).order_by("-date_created")`. The name is written once, when push is turned on, from the request's user agent, into `WebPushDevice.name`. The kind is read back from that name. |
| Which row is the browser in use | The page's script reads `pushManager.getSubscription()` and compares its endpoint with each row's. Only the browser knows its endpoint. |
| The browser's own state | The script: no service worker or `PushManager` → cannot receive push; an iPhone or iPad browser not started from the Home Screen and without `PushManager` → Home Screen; `Notification.permission === "denied"` → blocked; a subscription the server lists → on; otherwise → offer. |
| Turning push on | The script registers the package's service worker, asks permission inside the button's click handler, subscribes with the site's public key, and posts the subscription as JSON to a view that stores it (one per person and endpoint) and sends a test push. |
| Stopping | A POST per row to a view that deletes only the signed-in person's own subscription and adds a message naming it. For the browser in use, the script unsubscribes in the browser before submitting. |
| The success message after turning on | The subscribe view sets a session flag that the preferences page reads once. |

Every item under "What the sketch faked" in `sketch.md` is replaced by a task in `tasks.md`.

## Decisions research had to settle

### Push is an extra of its own

pywebpush, which django-push-notifications' web push extra installs, brings `aiohttp`,
`cryptography`, `requests`, `http-ece` and `py-vapid`. A project that uses notifications without
push would carry all of them, which G2 rules out. Push therefore becomes a fifth extra, `push`,
with its own integration module, `mvp_community.integrations.push`. The extra also names
django-generic-notifications, since push is a channel of it. The brainstorm's placement inside
`notifications` predates any look at the dependency tree. This amends decision D1.

### The public key is derived, not configured

The browser subscribes with the site's public key. django-push-notifications reads only the
private key (`WP_PRIVATE_KEY`) and the claims (`WP_CLAIMS`). py-vapid, already installed with
pywebpush, derives the public key from the private one (`Vapid01.from_file` or `from_string`,
then `public_key`), the same way pywebpush loads the key to sign. A host project therefore sets
the two settings django-push-notifications documents and nothing more.

### The service worker is a template served by a view

A service worker must come from the site's own origin. It is a template,
`mvp_community/push/worker.js`, served by a view under the package's URLs with a JavaScript
content type, so a project overrides it like any other template. It registers at its default
scope, the path it is served from, so it never replaces a project's own worker at `/`. Push
events and notification clicks reach a registration whatever its scope; scope governs only
which page loads the worker controls, and this worker controls none.

Not confirmed: whether an iPhone or iPad delivers push to a Home Screen web app through a worker
registered below the root. Apple documents push for Home Screen web apps without stating a scope
requirement. The documentation says that a project whose web app already has a worker at `/`
can import this one into it instead (`importScripts`).

### What a push carries and where it leads

The payload is JSON: the notification's subject as the title, its text as the body (cut to stay
well inside the 4 KB push services accept), and the path of the existing open view,
`mvp_community_notifications:open`. That view already marks the notification read and redirects
to its address, or to the notifications page when it has none (FR-008). The worker opens the path
against its own origin. The test push carries the preferences page's path.

### Language

The push channel has its own `recipient_language`, returning `LANGUAGE_CODE`, as the email
channel's does. A project that stores a language per person overrides both. This refines D8.

### Naming a browser

ua-parser (maintained, the parser behind most user-agent libraries) reads the request's user
agent: the browser family without a leading "Mobile ", then "on", then the device family for an
iPhone or iPad and the operating system otherwise ("Safari on iPhone", "Chrome on Android",
"Firefox on Windows"). An unreadable user agent gives "Unknown browser". The device kind for the
row's icon follows from the second part: iPhone and Android are phones, iPad is a tablet,
anything else a computer.

## What already exists

| New piece | Where the search stopped |
|---|---|
| Storing subscriptions, sending a push, retiring gone ones | Installed package: django-push-notifications (`WebPushDevice`, `send_message`) |
| A channel class | Installed package: django-generic-notifications (`BaseChannel`) |
| Marking read on tap and falling back to the list | This repo: `OpenNotificationView` |
| Deriving the public key | Installed package: py-vapid (`Vapid01`) |
| Reading a user agent | Maintained package: ua-parser (`ua_parser.parse`) |
| The card, list, rows, alerts, buttons | daisy-cotton and django-mvp components, as in the approved sketch |
| Asking permission, subscribing, showing a push | The browser: Notifications API, Push API, service workers |
| Subscribe view, stop view, worker view | New code: no installed package offers them without Django REST framework |
| Channel subclass, key derivation helper, browser-name helper, system check | New code, each a few lines over the packages above |
| The script that drives the card | New code: no component does it |
