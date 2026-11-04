# Brainstorm

Working notes from the package's first planning session. Nothing here is a
ratified decision.

## What the package is

The django-mvp layer around established packages for notifications, push,
reminders, email and activity feeds: templates, Cotton components, menu entries,
Account Center pages and settings. Code is limited to the helpers that connect
one package to another.

## Shape

- One Django app, `mvp_community`. A second app only if a need forces one.
- Each feature is an install extra:
  - `notifications`: notifications, web push and reminders
  - `mail`: translated email templates, digests, one-click unsubscribe, a delivery log
  - `activity`: an activity feed and a follow button
  - `sharecards`: generated preview images for shared links
  - `comments`, later
- No models of its own. Code that imports an extra's package lives in a module
  of its own, imported by the project when it wants that feature, as django-mvp's
  integrations are.

## Packages each feature builds on

| Extra | Packages |
|---|---|
| notifications | django-generic-notifications, django-push-notifications (web push), django-celery-beat, django-recurrence |
| mail | django-post-office, django-anymail |
| activity | django-activity-stream |
| sharecards | Playwright, django-meta |
| comments | django-comments-xtd, once version 3 is released |

Push subscriptions need a model, which django-push-notifications provides
(`WebPushDevice`). Notifications reach it through a delivery channel for
django-generic-notifications.

## Prior art

No package puts a styled interface on these packages for any Django UI
framework. The upstream packages leave it to the project:

- django-generic-notifications ships templates only in its example project.
- django-activity-stream ships bare, unstyled templates.
- django-post-office ships templates for the admin only.
