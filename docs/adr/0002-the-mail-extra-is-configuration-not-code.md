# ADR 0002 — The mail extra is configuration, not code

**Status:** accepted

## Decision

The `mail` extra installs django-post-office and django-anymail and adds no Python to the package: no integration module, no email backend, no sending function and no admin of its own. A host project switches it on with settings alone, `EMAIL_BACKEND = "post_office.EmailBackend"` and a django-anymail backend under `POST_OFFICE["BACKENDS"]`, as the Mail documentation describes. The demo project carries exactly that configuration, and the suite tests it by reading the demo's own settings.

What happens to an email after the provider accepts it is not recorded. Stored templates extend django-mvp's email layout in plain markup, without django-mvp's email components.

## Why

django-post-office plugs in as the project's email backend, so every email the project sends, from allauth, the django-mvp packages or its own code, is queued and logged without any of them importing it. Code here could only wrap what the two packages already do (Article XII). The two gaps that code could have closed both needed more than wiring. Joining provider delivery reports to the log needed a model of the package's own, because django-post-office keeps one status per email and discards the provider's message id, and django-anymail receives no reports from some providers. Making django-mvp's email components work in stored templates needed a template engine of the package's own, because django-post-office renders stored templates from a string and Cotton compiles only templates it loads from files.

The same reasoning kept the extra out of django-mvp core: no package that sends email needs django-post-office installed, and core already holds the layout every email uses.

## Revisit if

A provider's delivery reports become something projects using this package need from the admin, or django-post-office starts storing the provider's message id per recipient, which would let a small integration module record the reports without a model.
