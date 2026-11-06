# Decisions: Notifications by email, and digests

## D1 — The unsubscribe is built here, not in the mail feature

**Decision:** one-click unsubscribing is part of this feature. The roadmap's R4 entry is corrected to say so.
**Why:** the mail feature (specs/003-mail-queue-and-delivery-log) deferred unsubscribing to this item, so nothing had built it.
**ADR:** none — a roadmap scoping decision, recorded in the roadmap itself.

## D2 — The suggestions in the agreed reading are in scope

**Decision:** a page for the unsubscribe link to land on, no empty digests, and no notification already read on the site in a digest are requirements (FR-007, FR-012).
**Why:** the reading that suggested them was confirmed without changes on 2026-11-06.
**ADR:** none — follows from the spec.

## D3 — Digests and the unsubscribe stay in one feature with email

**Decision:** they are stories of this feature, not features of their own.
**Why:** a digest is how often the email channel reaches a person, and an unsubscribe turns that channel off.
**ADR:** none — a scoping decision for this feature.

## D4 — Always-sent types offer no frequency and are emailed at once

**Decision:** a type the project always sends on some channel offers no choice of how often, and its email is sent as it happens whatever frequency is stored (FR-016).
**Why:** Sam, at the sketch review: system and security notices must not wait for a digest.
**ADR:** none — follows from the spec.

## D5 — The frequency choice is disabled, not hidden, while email is off

**Decision:** the select is disabled while email is off for a type, and a hidden input carries the person's choice so saving keeps it.
**Why:** Sam, at the sketch review: hiding it shifted the page. A disabled control is not submitted, so without the hidden input saving would reset the choice.
**ADR:** none — a detail of one template.

## D6 — The unsubscribe link asks before it acts

**Decision:** following the link opens a confirmation page and changes nothing. The mail app's header posts and is the one-click route.
**Why:** mail security scanners open every link in an email (Sam, 2026-11-06).
**ADR:** none — follows from the spec.

## D7 — The library's System Message type is removed

**Decision:** the notifications extra unregisters it (FR-017). The demo's security notices are always sent by email instead of on the site.
**Why:** nothing in the library depends on it, it is English only, and it would appear in every project. Email is where a new-sign-in warning reaches someone who is not on the site.
**ADR:** docs/adr/0003-the-notifications-extra-registers-its-own-email-channel.md

## D8 — The package's email channel replaces the library's, guarded by a system check

**Decision:** a subclass of the library's `EmailChannel` is registered under `email` when the mail extra is installed, and none without it. Check `mvp_community.E001` reports a type naming the library's class.
**Why:** a subclass is the only route to the unsubscribe headers and the language without copying the library's rendering, and the library compares channel classes by identity.
**ADR:** docs/adr/0003-the-notifications-extra-registers-its-own-email-channel.md

## D9 — The channel calls the library's rendering rather than copying it

**Decision:** `send_now` and `send_digest` set the email's link on the instance and call the parent inside `translation.override`. The templates use two tags.
**Why:** copying about 130 lines of the library's rendering would drift from it on every release.
**ADR:** docs/adr/0003-the-notifications-extra-registers-its-own-email-channel.md

## D10 — Emails are written in LANGUAGE_CODE unless the project overrides recipient_language

**Decision:** "the recipient's language" in the spec is delivered through one method a project overrides.
**Why:** Django has no language per person.
**ADR:** docs/adr/0003-the-notifications-extra-registers-its-own-email-channel.md

## D11 — Unsubscribe links do not expire

**Decision:** links are signed, not timed. A link is read against the current types, so it never turns off a type now always sent by email, and a link whose every type is now always sent reads as invalid.
**Why:** RFC 8058 expects the header to keep working long after the email arrives.
**ADR:** none — local to the unsubscribe address.

## D12 — The unsubscribe view is login_not_required

**Decision:** the view carries Django's `login_not_required`.
**Why:** projects using `LoginRequiredMiddleware` would otherwise send the link to a sign-in page.
**ADR:** none — local to one view.

## D13 — configure registers with force=True

**Decision:** every registration in `configure` is forced.
**Why:** the registry skips a class it has seen before, even after an unregister, so `configure` could not be called twice.
**ADR:** none — local to one function.

## D14 — The one-click header needs a django-anymail provider backend

**Decision:** the documentation says the `List-Unsubscribe` header reaches mail apps intact only through a django-anymail provider backend. Over Django's SMTP backend the footer link is the way to unsubscribe.
**Why:** Python's email package folds a header value longer than a line, with no spaces to break at, into RFC 2047 encoded words, and the signed address is always longer than that. django-anymail passes headers to the provider unfolded, checked with its test backend. The mail extra already routes email through django-anymail.
**ADR:** none — a limit of Django's SMTP path, recorded in the documentation.
