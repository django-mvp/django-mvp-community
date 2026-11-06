# Sketch: Notifications by email, and digests

## What exists

- **Preferences.** django-generic-notifications stores, per person and notification type, whether
  each channel is on (`NotificationTypeChannelPreference`) and how often its email comes
  (`NotificationFrequencyPreference`). Its `get_notification_preferences` already returns each
  type's frequency, and `save_notification_preferences` already reads a `<type>__frequency` field.
  The preferences page renders one toggle per installed channel and ignores the frequency.
- **The email channel.** `EmailChannel` is registered whenever django-generic-notifications is
  installed, so the email column already shows on the preferences page with the notifications
  extra alone. It sends one email at once, or leaves the notification for a digest, from the
  person's frequency for that type. `send_notification_digests` sends a frequency's digests by key.
- **Frequencies.** Real-time and daily ship with the package. Weekly does not.
- **Email templates.** None ship. The channel looks templates up under
  `notifications/email/realtime/` and `notifications/email/digest/`, and falls back to the
  notification's own subject and text in plain email.
- **Layout.** django-mvp's `mvp/email/base.html` and its `c-mvp.email.*` components (text,
  button, divider, note) draw every other email the project sends.
- **Components.** The preferences page uses `c-table`, `c-form.toggle`, `c-mvp.card`,
  `c-mvp.text` and `c-button`. `c-form.select` from daisy-cotton fits the frequency choice. The
  unsubscribe page is a plain page on `page_view.html` with a `c-mvp.card` and a `c-button`.
- **No planning notes.**

## What the screens need from the code

- The preferences page needs the list of registered frequencies, each with a translated label,
  and each type's current frequency.
- The preferences page needs the email column only when the mail extra is installed.
- Every notification and digest email needs an unsubscribe address that names the person and
  the notification types the email covered, signed so it cannot be altered.
- The digest needs each group's notification type name from its key.
- The unsubscribe page needs to know whether the link was valid, whether anything was turned
  off, and which types it covered.
- A mail app's one-click unsubscribe needs a POST to the same address to turn the email off with
  no page.
- Email links need the site's own address, so the demo's site domain must be the address the
  pages are served on.

## What the sketch faked

- No unsubscribe header is added to the emails. Only the link in the footer exists.
- The weekly digest is registered when the notifications extra's package is imported, wherever
  that happens first.
- The unsubscribe link does not expire and is not tied to the person's current email address.
- Types the host project always sends by email still get an unsubscribe link in their emails.
- The email column is shown with the notifications extra alone, as before this feature.
- The demo's site domain was changed in the demo database by hand.
- `seed_notification_email` creates notifications and calls the channel's send methods directly,
  bypassing the person's preferences.
- The views, the template tags and the unsubscribe change were written without tests.

## What was ruled by eye

- The frequency choice sits under each type's name and description, labelled "By email", rather
  than in a column of its own: a fourth column did not fit at phone width.
- The frequency choice stays enabled when email is off for a type, so the choice is kept for
  when email is turned back on.
- Real-time is labelled "As it happens".
- The unsubscribe page names each type that was turned off in a card, and says the site is
  unchanged.
- The digest groups notifications by type, each group under its type's name, newest first.
- The digest's subject says "Today" or "Your week" with the count.
- The email footer says why the email was sent, then "Unsubscribe" and "Notification
  preferences" as two links.
