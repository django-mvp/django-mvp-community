# Research: Notifications by web push

The investigation for the plan is written here when the feature is planned. This file holds, for
now, what the specification assumes already works and whether it does.

## Assumptions checked

- **django-push-notifications runs on the Django versions this package supports.** Its package
  metadata lists Django up to 4.0 only, but its latest release (3.3.0, 2025-11) installs with its
  web push extra on Django 6.1.3, migrates, and reports no missing migrations under
  `makemigrations --check`. Confirmed.
- **It stores what a push subscription needs.** `WebPushDevice` has `user`, `name`, `active`,
  `date_created`, `registration_id`, `p256dh`, `auth` and `browser`, which covers the list of a
  person's subscriptions (FR-012) and sending to each. Confirmed.
- **It retires a subscription the push service reports as gone.** `webpush_send_message` sets
  `active = False` on a 404 or 410 response from the push service (FR-014). Confirmed by reading the
  installed source.
- **A new channel appears on the preferences page by itself.** `PreferencesView` passes
  `registry.get_all_channels()` to the template, which draws a column per channel
  (`mvp_community/integrations/notifications/views.py`). A push channel registered with
  django-generic-notifications is listed without changes to the page. Confirmed by reading the
  view; the column's behaviour with a third channel is confirmed when the sketch runs.
- **Subscribing from the browser.** django-push-notifications' own endpoint for storing a
  subscription is built on Django REST framework, which this package does not depend on. The
  browser hands the subscription to a view among the notifications extra's URLs instead. To be
  settled at planning.
