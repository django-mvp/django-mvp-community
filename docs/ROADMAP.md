# Roadmap — django-mvp-community

**Date:** 2026-11-04

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md)
for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor: some take several releases, and one release can move two. Once `1.0`
ships, a breaking change never goes out as `1.x` — it waits for the next major.

*Aspirational goals may be developed against v2 or v1 as required.*

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — Features install one at a time

*delivered in [#5](https://github.com/django-mvp/django-mvp-community/issues/5) · advances G2, G3*

The base install depends on Django and django-mvp alone, and code that imports an extra's
packages lives only in `mvp_community.integrations.<extra>`. A test imports every other module
with each extra's packages blocked, so a module that reaches for one fails the suite even where
the extra is installed. The README covers installing an extra and overriding any template by
name. Each extra's packages, pages and URLs arrive with the item that builds its feature.

Serves G2 and G3.

### R2 — Email that looks like the application

*feature · advances G4*

Notifications, digests and reminders all reach people by email, so branded, translated email is
the base the notification items build on. It builds on django-mvp's own base email layout, so the
project's other mail and this package's mail look the same.

**Deliverables:**
- Email the host project sends through the mail extra carries the project's look and is sent in
  the recipient's language.
- Email templates can be edited and translated per language without a code change.
- Every non-essential email can be unsubscribed from in one click, from the email itself.
- Staff can see what was sent, to whom, and whether it was delivered.

Serves G4. Out of scope: choosing or running a mail provider, and campaign or newsletter tools.

### R3 — Notifications on the site

*feature · advances G1, G3*

The bell, the unread count and the notifications page are the package's first reason to exist.
A person sees what happened, marks it read, and chooses which kinds of notification they want.

**Deliverables:**
- A bell in the application shell showing the person's unread count, kept current without a page
  reload.
- A notifications page listing a person's notifications, newest first, with read and unread
  states and a way to mark all read.
- A notification preferences page in the Account Center where a person turns each notification
  type and channel on or off.
- Every page and component above can be replaced by overriding one template.

Serves G1 and G3. Out of scope: deciding when a notification is sent, which belongs to the host
project.

### R4 — Notifications by email, and digests

*feature · advances G1, G4*

Joins the two previous items: a notification a person chose to receive by email arrives as
email, and someone who prefers fewer emails gets a daily or weekly digest instead.

**Deliverables:**
- Email as a notification channel, honouring each person's preferences.
- A daily and a weekly digest a person can choose instead of one email per notification.
- Digest and notification emails carry the one-click unsubscribe from R2.

Serves G1 and G4. Out of scope: push and reminders.

## Expected goals: v1.0.0

What a complete, dependable version is expected to have.

### R5 — Web push

*feature · advances G5*

Notifications reach a person's browser or installed web app as push, through the same
preferences. Includes the subscribe and unsubscribe controls, and the explanation people need
before a phone will accept push from a web app.

### R6 — Reminders on a person's own schedule

*feature · advances G6*

A person chooses when to be reminded, such as weekdays at 7pm, and the reminder arrives then in
their timezone, through the channels they chose. Needs R3 to R5.

### R7 — Activity feeds and following

*feature · advances G7*

A project shows what happened as a feed, and a person follows other people and objects to see
their activity. Includes the follow control, the feed component and a "following" page in the
Account Center.

## Aspirational goals: v2.0

Genuine wants whose absence never makes the package incomplete.

### R8 — Share images for shared links

*feature · advances G8*

A link to a page shows a generated preview image of that page when shared, made in the
background and kept until the page changes.

### R9 — Comments

*feature · advances G9*

People comment on any page or object, with replies, reporting and reactions. Waits until the
package it would build on has a stable release line.
