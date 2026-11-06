# Decisions: Notifications by email, and digests

## The unsubscribe is built here, not in the mail feature

The roadmap's R4 entry says notification email carries "the one-click unsubscribe from R2". The
mail feature (specs/003-mail-queue-and-delivery-log) deferred unsubscribing to this item, so
nothing has built it. It is part of this feature. The R4 entry is corrected when this feature
merges.

## The three suggestions in the agreed reading are in scope

The reading agreed on 2026-11-06 suggested a page for the unsubscribe link to land on, never
sending an empty digest, and leaving out of a digest what the person already read on the site. The
reading was confirmed without changes, so all three are requirements (FR-007, FR-012).

## Digests and the unsubscribe stay in one feature with email

A digest is how often the email channel reaches a person, and an unsubscribe turns that channel
off. Neither is a way of using the site apart from notification email, so they are stories of this
feature, not features of their own.

## The glossary gains "unsubscribe link"

CONTEXT.md is changed with the build, since this branch carries only the specification until it is
approved.

## Rulings at the sketch review (2026-11-06)

- Types the host project always sends on some channel (system messages, security notices) are
  always emailed as they happen and offer no choice of how often (FR-016).
- The choice of how often is hidden while email is off for a type (FR-005).
- The unsubscribe link opens a confirmation page and changes nothing by itself, because mail
  security scanners open every link in an email. The mail app's header is the one-click route
  (FR-009, FR-012).
- django-generic-notifications' built-in System Message type is removed by the notifications
  extra (FR-017). Nothing in the library depends on it and its documentation gives no reason for
  registering it by default. It is English only and would appear in every host project.
- The demo's security notices are always sent by email instead of on the site: email is where a
  new-sign-in warning reaches someone who is not on the site.
