# Decisions

## Scope taken from the roadmap

R2 as written lists the look of email, translated and editable templates, one-click unsubscribe and a delivery log. Since R2 was written, django-mvp 0.34.0 shipped its email layout, so the look is django-mvp's and this feature only makes stored templates use it. One-click unsubscribe applies to bulk and notification email, which nothing here sends yet, so it moves to notification email (R4). R2's brief in `docs/ROADMAP.md` is rewritten to this scope in the feature's pull request.

## Self-resolved ambiguities

- **Which emails are editable.** Only email sent from a stored template. Email from allauth and the django-mvp packages keeps its file templates and is only queued and logged. Moving their wording into the database would mean changing how those packages send, which FR-002 rules out.
- **Who sends the queue.** The host project, through django-post-office's own command or task. This package runs no worker, so it adds no scheduler dependency to the mail extra.
- **"Delivered".** The log records whether the provider accepted each email, when, and why it failed. Provider reports of what happened afterwards are out of scope (approved spec revision, 2026-11-06). django-post-office keeps one delivery status per email, not per recipient, and updates it from no report by default. The provider's message id, which django-anymail's reports refer to, is discarded when django-post-office sends. django-anymail has no report receiver for Scaleway. Joining reports to the log would need a model of this package's own, which the constitution rules out.
- **Where staff look.** django-post-office's admin pages. No page of this package's own.
- **Missing translation.** Revised during research: django-post-office raises when a template has no translation for the language asked for, before anything is queued, and offers no fallback. Writing a fallback would be a sending function of this package's own in front of django-post-office's, so the spec takes django-post-office's behaviour: sending in a language with no translation is refused, and the sending code chooses the template's own wording instead.
- **Layout words in the email's language.** django-post-office renders a stored template when it is queued, in whatever language is active. The documented way to send is inside `translation.override(language)`, so django-mvp's layout (its `lang` attribute and footer) is in the same language as the template's translation.

## Stored templates and django-mvp's email pieces

Settled in research. A stored template is rendered from a string, so `{% extends "mvp/email/base.html" %}` works and its `h1`, `p`, `ul` and `a` are styled by the layout, but django-mvp's Cotton email components do not compile (verified on django-cotton 2.8.0: the `<c-…>` markup reaches the email untouched). Making them work would need a template engine of this package's own that runs Cotton's compiler on every stored template. Not done: the documentation says stored templates are written in plain markup, and an email that needs the components stays a file template.

## US2 and US3 are written by the orchestrator, not dispatched

Each is one documentation section with no code and no test, because the admin pages they describe are django-post-office's. A dispatch would cost a brief, a worktree and a verify run to write two paragraphs.
