# Decisions

## Scope taken from the roadmap

R2 as written lists the look of email, translated and editable templates, one-click unsubscribe and a delivery log. Since R2 was written, django-mvp 0.34.0 shipped its email layout, so the look is django-mvp's and this feature only makes stored templates use it. One-click unsubscribe applies to bulk and notification email, which nothing here sends yet, so it moves to notification email (R4). R2's brief in `docs/ROADMAP.md` is rewritten to this scope in the feature's pull request.

## Self-resolved ambiguities

- **Which emails are editable.** Only email sent from a stored template. Email from allauth and the django-mvp packages keeps its file templates and is only queued and logged. Moving their wording into the database would mean changing how those packages send, which FR-002 rules out.
- **Who sends the queue.** The host project, through django-post-office's own command or task. This package runs no worker, so it adds no scheduler dependency to the mail extra.
- **"Delivered".** The log records whether the provider accepted each email, when, and why it failed. Provider reports of what happened afterwards are out of scope (approved spec revision, 2026-11-06). django-post-office keeps one delivery status per email, not per recipient, and updates it from no report by default. The provider's message id, which django-anymail's reports refer to, is discarded when django-post-office sends. django-anymail has no report receiver for Scaleway. Joining reports to the log would need a model of this package's own, which the constitution rules out.
- **Where staff look.** django-post-office's admin pages. No page of this package's own.
- **Language fallback.** A missing translation falls back to the template's own wording, which is django-post-office's behaviour.

## Open for research

- django-post-office renders a stored template from a string, not from a file. Extending `mvp/email/base.html` works from a string, but django-mvp's Cotton email pieces compile only in templates loaded from files. Research decides whether stored templates can use the pieces, or the documentation says they cannot.
