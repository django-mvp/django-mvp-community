# Research: Notifications by email, and digests

## Assumptions checked

Run on 2026-11-06 against the installed packages and the demo project.

- **The preferences page exists and lists installed channels.** The page renders and its 19
  tests pass. It reads the channel list from django-generic-notifications' registry, so a second
  registered channel appears as a second column with no change to the page's loop.
- **django-generic-notifications 2.4.0 ships an email channel with digest support.** Its
  `EmailChannel` sends one email at once or leaves the notification for a digest according to the
  person's frequency for that type, and its `send_notification_digests` command sends the digests
  that are due. The package stores per-type channel choices and per-type frequencies in its own
  models, so this feature needs no model.
- **It ships a daily frequency and a real-time one, not a weekly one.** Its documentation shows
  weekly as a frequency a project registers itself, in a few lines, and its digest command already
  sends any registered frequency by name. The weekly digest is registered by this package.
- **Its email goes through Django's `send_mail`**, so with the mail extra's `EMAIL_BACKEND` it is
  queued and logged by django-post-office. It sets no extra headers, so the unsubscribe header has
  to be added where the email is built.
- **It ships no email templates.** It looks the notification and digest templates up by name and,
  finding none, sends the notification's own subject and plain text. This package ships templates
  under those names that extend django-mvp's email layout, and a host project can override them in
  turn.

## Planning notes

There is no `planning-notes.md` for this feature.

## The sketch's needs and fakes

Each line of `sketch.md` under *What the screens need* and *What the sketch faked*, and how the
build meets it.

- **Frequencies with translated labels, and each type's current one.** django-generic-notifications'
  registry lists the frequencies and `get_notification_preferences` returns each type's current
  key. The labels are translated here, in the view, because the package's `name` values are not
  wrapped for translation.
- **The email column only with the mail extra.** django-generic-notifications registers its
  `EmailChannel` on import (`generic_notifications/channels.py:135`). The notifications extra
  replaces it with its own channel when `post_office` is installed, and unregisters it when it is
  not (`registry.unregister_channel`, `generic_notifications/registry.py:99`).
- **A signed unsubscribe address.** `django.core.signing` with a salt, held in one class that both
  makes and reads the address, so the emails, the header and the page agree.
- **Each digest group's type name.** The registry's `get_type(key)` returns the class; the tag the
  sketch added is replaced by passing names into the template context from the channel.
- **Whether a type is always sent on some channel.** `NotificationType.required_channels`.
- **The channel is named by identity.** django-generic-notifications checks `required_channels`
  and `default_channels` by class identity (`generic_notifications/types.py:133,146`,
  `preferences.py:61`), so a subclass registered under `email` does not match a type naming the
  library's class. Plan, *Set-up*, adds a system check.
- **The unsubscribe page's outcomes and the one-click POST.** The view reads the address through the
  class above. A mail app's one-click POST carries `List-Unsubscribe=One-Click` in its body
  (RFC 8058, section 3.1) and is answered with no page.
- **Email links on the site's own address.** django-mvp's `email_url` tag already makes them
  absolute from the request or the current `Site`. The demo's `seed_demo` sets the `Site` domain
  (below).
- **No unsubscribe header.** The channel adds `List-Unsubscribe` and `List-Unsubscribe-Post`
  (RFC 2369, RFC 8058) to each email it sends. django-post-office keeps `extra_headers` on the
  queued email (`post_office/backends.py:34`).
- **Weekly digest registered on first import.** Registration moves into the extra's set-up, called
  from the app's `ready`, so it happens once and in a known order.
- **Links that never expire.** An unsubscribe link has to keep working long after the email is
  read, which is what RFC 8058 expects of the header. It is signed, not timed. It names the person
  by primary key, so a changed email address does not matter, and a deleted account makes it
  invalid.
- **Fake: always-sent types carried an unsubscribe link.** Emails whose every type is always sent
  by email carry neither the link nor the header.
- **"Always as it happens" rests on the default frequency.** The channel sends an always-sent type
  at once whatever frequency is stored.
- **System Message removed on first import.** Same set-up as the weekly digest.
- **The demo's domain changed by hand.** `seed_demo` sets the `Site` domain from
  `DEMO_SITE_DOMAIN`, default `localhost:8000`, the address `manage.py runserver` serves.
- **`seed_notification_email` bypasses preferences.** It sends through `send_notification`, so the
  demo's emails follow the seeded preferences, then sends the due digests.
- **No tests.** Every behaviour is rebuilt test-first.

## Language

Django has no per-person language. The channel renders each email inside
`translation.override` with the language its `recipient_language` method returns, which is
`settings.LANGUAGE_CODE` unless a project subclasses the channel. This keeps a single extension
point, a class with one method to override, as Article X asks, and adds no setting. The
documentation shows the override for a project that stores a language on its users.

## What already exists

- weekly frequency · 7, new · `generic_notifications.frequencies.BaseFrequency` subclass, as the
  package's own documentation shows
- removing System Message · 3, package · `registry.unregister_type`
- email channel with templates, digest and preferences · 3, package · `generic_notifications.channels.EmailChannel`
- sending due digests · 3, package · `send_notification_digests` management command
- the unsubscribe headers on an email · 4, Django · `EmailMultiAlternatives(headers=...)`
- signing the unsubscribe address · 4, Django · `django.core.signing.dumps` / `loads`
- turning email off for a type · 3, package · `NotificationType.disable_channel`
- whether a type reaches a person by email · 3, package · `NotificationType.get_enabled_channels`
- absolute links in emails · 3, package · `mvp.templatetags.mvp_email.email_url`
- the email layout and its parts · 3, package · `mvp/email/base.html`, `c-mvp.email.*`
- the frequency select and the joined label · 3, package · daisy-cotton `c-form.select`, `c-join`
- disabling the select while email is off · 3, package · Alpine.js, which django-mvp loads
- keeping a disabled select's value · 5, browser · a hidden input, since a disabled control is not
  submitted (HTML, "constructing the entry list")
- confirmation page · 3, package · `mvp.views.MVPTemplateView` and `page_view.html`
- the one-click request handling · 7, new · searched django-post-office, django-anymail and
  django-generic-notifications for `List-Unsubscribe`; none handles it
