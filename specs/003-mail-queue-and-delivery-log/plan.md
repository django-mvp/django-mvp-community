# Implementation Plan — 003 Queue, log and send a project's email through the mail extra

**Branch**: `003-mail-queue-and-delivery-log` · **Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md)

## Summary

The mail extra brings django-post-office and django-anymail. A project installs it, applies four settings and gets every email queued, logged and sent through its provider. This package adds no Python: the work is the extra's dependencies, the demo configured as the documentation says, tests that hold the documented configuration to its promises, and the documentation.

## Technical Context

Python 3.12 and 3.13, Django 5.2, 6.0 and 6.1. django-post-office ≥ 3.12, django-anymail ≥ 13. Tests with pytest-django on the demo's settings, through `tests/settings.py`.

## Constitution Check

- Article XII (scope): no models, no migrations, no sending logic. Pass.
- Article XIII (extras): the extra's packages are imported only by the demo and the tests. The base-install test derives the blocked packages from the extra's metadata, so it covers the new ones unchanged. Pass.
- Article XIV (templates before code): no code at all. Pass.
- Article VIII (i18n): no user-facing strings of this package's own. Pass.
- Article VI (documentation): a new page, `docs/developer/mail.md`, linked from the README.

## Design

### The extra

`mail = ["django-post-office>=3.12", "django-anymail>=13"]` in `pyproject.toml`, and `mail` added to the development extras so the demo and the suite run it. deptry: both are imported by nothing in the package, so they join `DEP002` with the reason.

### The demo

`demo/settings.py` applies the documented configuration: `post_office` in `INSTALLED_APPS`, `EMAIL_BACKEND = "post_office.EmailBackend"`, `POST_OFFICE_TEMPLATE_CACHE = False` (django-post-office clears the wrong cache key when a translation is saved, so with the cache on a staff edit to a translation is not used for up to five minutes: `post_office/models.py:352` deletes `name`, `post_office/utils.py:62` reads `name:language`), and `POST_OFFICE` with `DEFAULT_PRIORITY = "now"` so the demo needs no queue runner, and `BACKENDS["default"]` read from the environment: SMTP when `DEMO_EMAIL_HOST` is set (the development server sends to a Mailpit inbox), the console otherwise. The demo's existing `EMAIL_BACKEND` line is replaced. `demo/urls.py` mounts the admin at `admin/`, so the log and the stored templates can be seen with the seeded superuser.

`demo/management/commands/seed_mail.py` (DEBUG only, like the other seeds): creates the stored template `welcome`, extending `mvp/email/base.html`, with a German translation whose own `{% block footer %}` is written in German (django-mvp ships no German catalogue, so the layout's default footer would stay English), and sends it once in English and once in German so the log has entries. Run by `seed_demo`'s documentation alongside the other seeds.

### Tests

In `tests/test_demo.py`, a `TestMail` class. Its fixture builds the settings from the demo module's own values, `override_settings(EMAIL_BACKEND=demo.settings.EMAIL_BACKEND, POST_OFFICE={**demo.settings.POST_OFFICE, "BACKENDS": {"default": "anymail.backends.test.EmailBackend"}})`, changing only the backend django-post-office hands email to and, per test, `DEFAULT_PRIORITY`. Removing the demo's lines then fails the tests. The hand-off goes to django-anymail's test backend, so the suite exercises the anymail path FR-003 relies on.

1. An email sent with `send_mail` is queued as a `post_office.Email` row and not handed to the backend during the call.
2. Sending the queue hands it to the configured backend and the row and its log read as sent.
3. With `DEFAULT_PRIORITY = "now"`, the email is handed over during the call and still logged.
4. A stored template extending the layout, sent with `language="de"` inside `translation.override("de")`, is written in the German translation, including its German footer, and in the layout (`lang="de"` on the root element, the layout's styles inlined).
5. A stored template sent with `language=` naming a language it has no translation for raises and writes no row.

What is not tested, per `docs/contributing/standards/testing.md`: the admin's pages, search and permissions, retries, failure logging, template validation, and the demo's seed command, which are django-post-office's behaviour or demo-only.

### Documentation

`docs/developer/mail.md`, how-to shaped like `notifications.md`:

1. Install the extra.
2. The settings: `INSTALLED_APPS`, `EMAIL_BACKEND`, `POST_OFFICE["BACKENDS"]`, `POST_OFFICE_TEMPLATE_CACHE = False` and why, `ANYMAIL` with one provider as the example, and `migrate`.
3. Send the queue: `send_queued_mail` on a schedule, the Celery task, or `DEFAULT_PRIORITY = "now"`. Retries. `cleanup_mail` on a schedule, because the log keeps each email's full body.
4. Check what was sent: the admin's email list, search by address, the status and the log of a failed email. What the log does not record: what happens after the provider accepts an email. The log holds full bodies, including one-time links such as password resets, so view permission on its models goes to trusted staff only.
5. Write a stored template: in the admin, extending `mvp/email/base.html`, in plain `h1`, `p`, `ul`, `a`; django-mvp's email components do not work here; a translation per language, each writing its own `footer` block where the layout's default would be in the wrong language.
6. Send a stored template from code: `mail.send(..., language=<code>)` inside `translation.override(<code>)`. The argument picks the translation and refuses a missing one; the override puts the layout's `lang` attribute in the same language.

README: the `mail` extra paragraph. CHANGELOG: an `Added` entry. CONTEXT.md: queued email, delivery log, stored template. `docs/ROADMAP.md`: R2's brief rewritten to this scope, its status from `roadmap-status --apply`.

django-mvp's `docs/developer/email.md` gains one paragraph pointing to this extra, in its own pull request on django-mvp.

### Story order

US1 → US2 → US3. US1 carries the extra, the demo, the tests and the first two documentation sections. US2 and US3 are each one documentation section, written directly by the orchestrator (`decisions.md`).
