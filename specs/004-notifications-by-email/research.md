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
- **It ships a daily frequency and a real-time one, not a weekly one.** Weekly is shown in its
  documentation as a frequency a project declares itself. The weekly digest is declared by this
  package.
- **Its email goes through Django's `send_mail`**, so with the mail extra's `EMAIL_BACKEND` it is
  queued and logged by django-post-office. It sets no extra headers, so the unsubscribe header has
  to be added where the email is built.
- **Its email templates are its own, not django-mvp's email layout.** The notification and digest
  templates are looked up by name, so this package can ship templates under those names that extend
  django-mvp's layout, and a host project can override them in turn.
