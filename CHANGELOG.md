# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
  Everything not yet released goes under [Unreleased], grouped by change type:
  Added, Changed, Deprecated, Removed, Fixed, Security. Prepare Release promotes
  that section to a version heading and dates it.

  Do NOT write a version heading by hand. Tag Release fires on any push to main
  that touches pyproject.toml, and the only thing stopping it cutting a release
  from that push is the absence of a `## [X.Y.Z]` section matching the version
  in pyproject.toml. Writing one here defeats that guard, and the repository
  ends up with a tag and a GitHub Release for a version nobody prepared.

  Write for someone deciding whether to upgrade. Say what changed for them and
  what they have to do about it, not which files moved.
-->

## [Unreleased]

## [v0.1.3] - 2026-11-09

### Fixed

- The notification preferences page and the following page sit under the Account Center's address.
  Both say in their breadcrumbs that they are in the Account Center, which django-mvp's URLs mount at
  `account/`, but they were served from `account-center/notifications/` and
  `account-center/following/`. They are now at `account/notifications/` and `account/following/`.
  Their URL names, `mvp_community_notifications:preferences` and `mvp_community_activity:following`,
  are unchanged, so links built with `{% url %}` or `reverse()` follow them. A link or bookmark
  written as the old address no longer resolves; point it at the new one.

## [v0.1.2] - 2026-11-09

### Fixed

- The notification preferences page fits a phone. With the site, email and push channels registered,
  the choice of how often email arrives widened the first column until the last channel's toggles
  sat off the edge of the card, so a person had to scroll sideways to reach them. That choice now
  sits on a line of its own under each type, spanning the table, and the channel columns are
  narrower, so every toggle is in reach at 360 pixels wide. A project that overrides
  `mvp_community/notifications/preferences.html` keeps its own layout.

## [v0.1.1] - 2026-11-09

### Fixed

- Notification email and digests are sent in a project whose user model has a UUID primary key.
  Building the unsubscribe link failed there, because the key was signed as a JSON value, so no
  notification email went out. The key is now signed as text. Links in email already sent keep
  working.
- An unsubscribe link whose signed key the user model cannot hold now opens the invalid-link page
  instead of failing with a server error.

## [v0.1.0] - 2026-11-09

### Added

- The package, generated and not yet doing anything.
- The `notifications` extra: a bell in the header showing the signed-in
  person's unread count, a notifications page with "Mark all read", and a
  notification preferences page in the Account Center, all built on
  django-generic-notifications. Install it with
  `pip install "django-mvp-community[notifications]"`.
- Notifications by email, with the `mail` extra installed: a person who chose
  email for a type receives it in django-mvp's email layout, written in the
  site's language (`NotificationEmailChannel.recipient_language` changes that),
  and a weekly digest beside the daily one. Name `NotificationEmailChannel` in
  a type's channels instead of django-generic-notifications' `EmailChannel`;
  system check `mvp_community.E001` reports any type that does not.
- Unsubscribing from notification email: every notification email and digest
  carries a link, and the `List-Unsubscribe` one-click header, that opens a page
  to turn email off for the types in that email. It works without signing in
  and does not expire. Types the project always sends by email carry no link.
- The `activity` extra, built on django-activity-stream: `ActivityFeedView`,
  a feed of the whole site or of one object that you mount at an address of
  your choosing, a following page in the Account Center, and components for
  recent activity, a follow control and a followers list. Install it with
  `pip install "django-mvp-community[activity]"`.
- The `mail` extra, built on django-post-office and django-anymail: every email
  your project sends is queued, logged with its full body and delivered through
  your provider, and stored templates extend django-mvp's email layout with a
  translation per language. It adds no code of its own; the new Mail page
  documents the settings. Install it with
  `pip install "django-mvp-community[mail]"`.
- The `push` extra, built on django-push-notifications and py-vapid: a person
  can get their notifications as push messages in their browser, even when the
  site is closed. The notification preferences page gains a push card that
  turns push on for the browser in use, lists the browsers receiving push and
  stops them one at a time, and `PushChannel` sends a push to each of them. Name
  `PushChannel` in a type's channels and set `WP_PRIVATE_KEY` and `WP_CLAIMS`.
  Install it with `pip install "django-mvp-community[push]"`.

### Changed

- Notification preferences no longer list django-generic-notifications'
  "System Message" type, and without the `mail` extra installed the email
  column is not drawn. Register your own type if you want a system message.
