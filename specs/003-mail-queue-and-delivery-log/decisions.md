# Decisions: Queue, log and send a project's email through the mail extra

## D1 — Scope taken from the roadmap

**Decision:** the feature delivers the queue, the log and stored, translated templates. The look is django-mvp's email layout, shipped in django-mvp 0.34.0 after R2 was written. One-click unsubscribe moves to notification email (R4), and R2's brief is rewritten to this scope.
**Why:** unsubscribe applies to bulk and notification email, which nothing here sends yet (Sam, 2026-11-06).
**ADR:** none — a roadmap scoping decision, recorded in the roadmap itself.

## D2 — Only stored templates are editable

**Decision:** only email sent from a stored template can be edited in the database. Email from allauth and the django-mvp packages keeps its file templates and is only queued and logged.
**Why:** moving their wording into the database would change how those packages send, which FR-002 rules out.
**ADR:** none — follows from the spec.

## D3 — The project sends the queue

**Decision:** the package runs no queue worker. The host project uses django-post-office's command, its Celery task, or `DEFAULT_PRIORITY = "now"`.
**Why:** a worker here would add a scheduler dependency to the extra for something django-post-office already offers.
**ADR:** docs/adr/0002-the-mail-extra-is-configuration-not-code.md

## D4 — No delivery reports

**Decision:** the log records whether the provider accepted each email, when, and why it failed. Nothing after that is recorded.
**Why:** django-post-office keeps one status per email and discards the provider's message id, and django-anymail has no report receiver for some providers, Scaleway among them. Joining reports to the log needs a model of this package's own, which the constitution rules out. Sam, 2026-11-06: per-recipient bounce figures belong to a dedicated mail service.
**ADR:** docs/adr/0002-the-mail-extra-is-configuration-not-code.md

## D5 — The admin is django-post-office's

**Decision:** staff read the log and edit stored templates in django-post-office's admin pages. No page of this package's own.
**ADR:** none — follows from the spec.

## D6 — A missing translation is refused

**Decision:** sending a stored template in a language it has no translation for raises, and nothing is queued. The spec was revised to match.
**Why:** django-post-office raises `EmailTemplate.DoesNotExist` before writing anything and offers no fallback. A fallback would be a sending function of this package's own.
**ADR:** none — django-post-office's behaviour, documented on the Mail page.

## D7 — Sending names the language twice

**Decision:** the documented way to send a stored template passes `language=` and runs inside `translation.override`. Each translation writes its own `footer` block.
**Why:** the argument picks the translation, the override sets the layout's `lang` attribute, and django-mvp ships no catalogue, so the layout's default footer is English (design review).
**ADR:** none — usage documented on the Mail page.

## D8 — Stored templates do not use django-mvp's email components

**Decision:** stored templates are written in plain markup on `mvp/email/base.html`. An email that needs the components stays a file template.
**Why:** django-post-office renders stored templates from a string, and Cotton compiles only templates it loads from files (verified on django-cotton 2.8.0). Making them work would need a template engine of this package's own.
**ADR:** docs/adr/0002-the-mail-extra-is-configuration-not-code.md

## D9 — The template cache is off

**Decision:** the documented settings, and the demo, set `POST_OFFICE_TEMPLATE_CACHE = False`.
**Why:** django-post-office clears the cache entry for the template's name when a translation is saved, but reads the entry for name and language (`post_office/models.py:352`, `post_office/utils.py:62`), so a staff edit to a translation would be ignored for up to five minutes. FR-009 and SC-003.
**Revisit if:** django-post-office clears the right key.
**ADR:** none — a setting with its reason on the Mail page.

## D10 — The tests read the demo's settings

**Decision:** the mail tests build their settings from `demo.settings` and hand email to django-anymail's test backend.
**Why:** a test that restated the configuration would stay green with the demo's lines removed (design review).
**ADR:** none — a test arrangement.

## D11 — Untested by design

**Decision:** no tests for the admin pages, their search and permissions, retries, failure logging, template validation or the demo's `seed_mail` command.
**Why:** they are django-post-office's behaviour or demo-only, per `docs/contributing/standards/testing.md` section 1.
**ADR:** none — follows the testing standard.

## D12 — US2 and US3 written directly

**Decision:** stories 2 and 3 were written by the orchestrator, not dispatched.
**Why:** each is one documentation section with no code and no test.
**ADR:** none — how the work was done, not what it is.
