# Decisions

## Scope taken from the roadmap

R2 as written lists the look of email, translated and editable templates, one-click unsubscribe and a delivery log. Since R2 was written, django-mvp 0.34.0 shipped its email layout, so the look is django-mvp's and this feature only makes stored templates use it. One-click unsubscribe applies to bulk and notification email, which nothing here sends yet, so it moves to notification email (R4). R2's brief in `docs/ROADMAP.md` is rewritten to this scope in the feature's pull request.

## Self-resolved ambiguities

- **Which emails are editable.** Only email sent from a stored template. Email from allauth and the django-mvp packages keeps its file templates and is only queued and logged. Moving their wording into the database would mean changing how those packages send, which FR-002 rules out.
- **Who sends the queue.** The host project, through django-post-office's own command or task. This package runs no worker, so it adds no scheduler dependency to the mail extra.
- **"Delivered".** Kept as two facts: accepted by the provider (always recorded) and reached, bounced or rejected (recorded when the provider reports it). Recording provider reports needs django-anymail's delivery reports joined to django-post-office's per-recipient status. django-post-office receives reports itself only from SES and SparkPost.
- **Where staff look.** django-post-office's admin pages. No page of this package's own.
- **Language fallback.** A missing translation falls back to the template's own wording, which is django-post-office's behaviour.

## Open for research

- django-post-office renders a stored template from a string, not from a file. Extending `mvp/email/base.html` works from a string, but django-mvp's Cotton email pieces compile only in templates loaded from files. Research decides whether stored templates can use the pieces, or the documentation says they cannot.
- Which providers django-anymail reports delivery for, and how a report is shown to come from the provider for each.
