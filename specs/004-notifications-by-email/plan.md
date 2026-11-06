# Implementation Plan — 004 Notifications by email, and digests

**Branch**: `004-notifications-by-email` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) · **Sketch**: [sketch.md](sketch.md)

## Summary

The notifications extra gains a notification email channel of its own, registered in place of
django-generic-notifications' when the mail extra is installed, and a weekly digest beside the
package's daily one. The preferences page offers each type a choice of how often its email comes.
Every notification and digest email carries a signed unsubscribe link and the one-click
unsubscribe headers, and the link opens a confirmation page. The screens and emails are the ones
approved in the sketch. The code behind them is rebuilt test-first.

## Technical Context

Python 3.12+, Django 5.2 to 6.1, django-generic-notifications 2.4, django-post-office 3.12,
django-mvp's email layout and components, daisy-cotton, Alpine.js through django-mvp. pytest with
pytest-django. No models and no migrations.

## Constitution Check

- **Article II, simplicity / VII, dependencies.** No new dependency. One channel class, one
  frequency class, one class for the unsubscribe address, one view.
- **Article X, cohesion.** Making and reading an unsubscribe address are one class,
  `UnsubscribeLink`. The channel's extension points are methods a project overrides by
  subclassing.
- **Article XII, scope.** The package decides nothing about who is notified or when. Removing
  django-generic-notifications' own System Message type keeps the preferences to the types the
  host project declares (FR-017).
- **Article XIII, extras.** Everything that imports django-generic-notifications or
  django-post-office stays in `mvp_community.integrations.notifications`. The set-up checks
  whether `post_office` is installed rather than importing it.
- **Article XIV, templates first.** Every email and page is a template a project overrides by
  name (FR-013).
- **Article VIII, i18n.** Every new string is translatable. Frequency labels are translated in the
  view.
- **Article XI, compatibility.** Without the mail extra the email column now disappears from the
  preferences page (FR-002). The package is pre-0.1.0, so this is noted in the CHANGELOG, not
  deprecated.

## Design

### Set-up (`integrations/notifications/setup.py`)

A class `NotificationsSetup` with one class method, `configure(mail_installed)`, called from
`MvpCommunityConfig.ready` with `apps.is_installed("post_office")`. It:

1. registers `WeeklyFrequency` (`frequencies.py`),
2. unregisters django-generic-notifications' `SystemMessage`,
3. unregisters the package's `EmailChannel`, and when the mail extra is installed registers
   `NotificationEmailChannel` (key `email`) in its place.

`configure` is idempotent, so the test suite can call it with either value and restore it.
The sketch's imports in the package `__init__` are removed.

### The channel (`integrations/notifications/channels.py`)

`NotificationEmailChannel(EmailChannel)`:

- `process(notification)`: a type with any required channel is sent at once, whatever frequency
  is stored (FR-016). Otherwise the parent's behaviour.
- `send_now` and `send_digest`: render inside `translation.override(self.recipient_language(user))`
  and pass the unsubscribe address and the types' names into the template context. The parent
  builds context itself, so these methods are overridden in full, keeping the parent's template
  lookup names and fallbacks.
- `recipient_language(user)`: `settings.LANGUAGE_CODE`. The documented extension point.
- `send_email(...)`: builds an `EmailMultiAlternatives` with `List-Unsubscribe` and
  `List-Unsubscribe-Post: List-Unsubscribe=One-Click` when the email has an unsubscribe address,
  and sends it through Django's mail backend, so django-post-office queues and logs it.
- An email whose types are all always sent by email has no unsubscribe address, no link and no
  headers.

### The unsubscribe address (`integrations/notifications/unsubscribe.py`)

`UnsubscribeLink`, holding a person and notification type keys:

- `for_email(user, type_keys)`: drops keys whose type always sends email. Returns `None` when none
  remain.
- `path` and `url(request_or_none)`: the signed address, absolute through the current `Site` when
  there is no request.
- `read(token)`: the person and the registered types, or `None` when the signature is bad, the
  person no longer exists or no named type is registered.
- `emailed()`: the types that still reach the person by email.
- `turn_off()`: `disable_channel(user, email channel)` for each, returning the ones changed.

The template tag from the sketch is removed: the templates receive the address in their context.

### The unsubscribe view

`UnsubscribeView(MVPTemplateView)`, CSRF-exempt, no sign-in. `GET` renders `confirm`, `already` or
`invalid`. `POST` with `List-Unsubscribe=One-Click` turns the email off and answers `200` with no
body, or `400` for an invalid address. Any other `POST` turns it off and renders `done`,
`already` or `invalid`. The approved template is kept.

### The preferences page

`PreferencesView` adds `frequencies` (key, translated label) and, per row, `offers_frequency`
(no required channel). The approved template is kept: the Alpine row state, the joined select and
the hidden input that carries the choice while email is off. `post` is unchanged:
django-generic-notifications' `save_notification_preferences` already reads `<type>__frequency`.

### Templates

The approved email templates under `notifications/email/` are kept. They read the address and the
type names from the context rather than the sketch's tags. The footer include shows the
unsubscribe link only when there is an address.

### The demo

- `demo/notifications.py`: security notices required on email, default frequency real-time.
- `seed_demo`: sets the `Site` domain from `DEMO_SITE_DOMAIN`, default `localhost:8000`.
- `seed_notification_email`: seeds preferences for the regular user, sends through
  `send_notification`, then sends the daily and weekly digests through
  `send_notification_digests`, and prints the unsubscribe addresses.

### Tests

New files mirror the source tree under `tests/test_integrations/test_notifications/`:
`test_setup.py`, `test_channels.py`, `test_unsubscribe.py`, and additions to `test_views.py` and
`tests/test_demo.py`. Email is asserted by recipient, headers and the data or link it carries,
never by wording (testing standard, *Text*).

US1:
1. With the mail extra, the email channel registered under `email` is the package's own; without
   it, no `email` channel is registered and the preferences page lists the site only.
2. The weekly frequency is registered; System Message is not.
3. A notification to a person with email on and real-time is queued in django-post-office's log
   to that person, with an HTML part extending the layout (the layout's root element is present).
4. Email off, or no address: nothing is queued.
5. Daily and weekly digests: one email per person with unread, unsent notifications of the types
   they chose for that frequency; none for a person with none; read notifications left out.
6. `recipient_language` is used: a subclass returning `de` renders with `lang="de"`.
7. A project template under the realtime name replaces the package's.
8. An always-sent type is sent at once even with a stored daily frequency.

US2:
9. The preferences page posts and stores a frequency per type; the select is absent for a type with
   a required channel; its row has the hidden input, disabled attribute bindings present (script
   hooks are tested).
10. A type with no stored choice shows its declared default selected.

US3:
11. `UnsubscribeLink` round trip; altered token, deleted person and unknown types read as invalid.
12. `for_email` drops always-sent types and returns `None` when nothing is left.
13. GET changes nothing; POST from the page turns email off for exactly the named types and leaves
    the site channel and other types alone; a second POST reports already off.
14. One-click POST answers 200 with no page and turns email off; an invalid token answers 400.
15. Notification and digest emails carry `List-Unsubscribe` with the address and
    `List-Unsubscribe-Post`; an email of only always-sent types carries neither, and no link.
16. A signed-out visitor can GET and POST the page.

### Documentation

`docs/developer/notifications.md`:
1. *Install notifications*: notification email needs the mail extra; without it the site is the
   only channel.
2. Rewrite *What django-generic-notifications adds by itself*: the package's channel replaces the
   library's, System Message is removed, a project that wants it registers its own type.
3. New *Send digests*: the daily and weekly commands and how to schedule them.
4. New *Unsubscribing*: the link, the confirmation page, the one-click header, which types carry
   none.
5. New *Email in the person's language*: subclassing the channel for `recipient_language`.
6. *Replace a template or component*: the email template names.
7. Remove *Why saving preferences clears digest frequencies*: the page now posts frequencies.

Also `README.md`, `CHANGELOG.md`, `CONTEXT.md` (unsubscribe link), and `docs/ROADMAP.md` (R4: the
unsubscribe is delivered here, not in R2).

### Story order

US1 → US2 → US3. US3's headers build on US1's channel.
