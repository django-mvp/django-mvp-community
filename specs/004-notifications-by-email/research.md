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
