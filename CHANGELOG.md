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

### Added

- The package, generated and not yet doing anything.
- The `notifications` extra: a bell in the header showing the signed-in
  person's unread count, a notifications page with "Mark all read", and a
  notification preferences page in the Account Center, all built on
  django-generic-notifications. Install it with
  `pip install "django-mvp-community[notifications]"`.
