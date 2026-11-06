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
