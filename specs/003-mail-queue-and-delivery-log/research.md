# Research — 003 Queue, log and send a project's email through the mail extra

Investigated against django-post-office 3.12.0, django-anymail 15.2, django-cotton 2.8.0 and django-mvp 0.34.0, installed on the feature branch.

## Planning notes

- **"Should a large portion of it be placed in django-mvp core?"** Not adopted, as agreed while specifying. django-post-office replaces the project's `EMAIL_BACKEND`, so no package that sends email imports it or needs it installed. django-mvp core keeps the email layout it already has. Its email page gains one paragraph pointing to this extra, in a separate pull request on django-mvp.
- **mjml-python, listed in the project feature document.** Not adopted. django-mvp's email layout does the job it was listed for.
- **"Ignore Scaleway… we are not trying to build a fully featured Mailchimp alternative."** Adopted: the feature records whether the provider accepted an email and nothing after that. The documentation names Scaleway only as one of django-anymail's providers.

## How the pieces fit

- `EMAIL_BACKEND = "post_office.EmailBackend"` turns every `send_mail`, `EmailMessage.send()` and allauth email into a queued `post_office.Email` row, whatever sends it. Nothing in the sending code changes.
- `POST_OFFICE["BACKENDS"]["default"]` names the backend django-post-office hands queued email to: a django-anymail backend such as `anymail.backends.scaleway.EmailBackend`, with the provider's keys under `ANYMAIL`. On Django 6.1, django-post-office also reads `MAILERS`, but the `EMAIL_BACKEND` form works on every supported Django version, so the documentation uses it.
- The queue is sent by `manage.py send_queued_mail` on a schedule, or by django-post-office's Celery task with `CELERY_ENABLED`. `POST_OFFICE["DEFAULT_PRIORITY"] = "now"` sends each email during the request instead, still writing the `Email` row and its `Log`. `MAX_RETRIES` and `RETRY_INTERVAL` retry failures.
- The admin is django-post-office's own: `Email` (searchable by `to` and `subject`, with its `Log` rows inline), `Log` and `EmailTemplate` (with translations inline when `USE_I18N` is on). Template fields are validated with `validate_template_syntax`, so a stored template that would not render is refused on save. Every admin page requires staff and the model permission.
- A stored template is sent with `post_office.mail.send(recipients, sender, template="name", language="de", context={...})`. It is rendered when it is queued, from a string, with the active language. A missing translation raises `EmailTemplate.DoesNotExist` before any row is written.
- Rendering from a string supports `{% extends "mvp/email/base.html" %}`, and the layout's inline styles are applied. Cotton components do not compile in a string (`<c-mvp.email.button>` arrives as raw markup). See `decisions.md`.
- `mail.send(..., language=<code>)` picks the translation (`post_office/mail.py:197-201`). Sending inside `translation.override(<code>)` as well puts the layout's `lang` attribute in that language. django-mvp ships no translation catalogue, so the layout's default footer stays English: a translation writes its own `footer` block.

## What already exists

- The queue, the log, retries, stored templates and translations: django-post-office. Nothing needed.
- The providers: django-anymail. Nothing needed.
- The email layout: django-mvp `mvp/email/base.html`. Nothing needed.
- The admin pages: django-post-office's `admin.py`. Nothing needed.
- Making every email go through the queue: Django's `EMAIL_BACKEND` setting. Nothing needed.
- Sending a stored template in a language: `post_office.mail.send` with `translation.override`. Nothing needed.
- Demo data, a stored template with a German translation and a few logged emails: new code, a demo-only management command in `demo/management/commands/`, the same shape as `seed_activity`.

No code is added to `mvp_community`. The extra is its dependencies, the documented settings and the documentation.
