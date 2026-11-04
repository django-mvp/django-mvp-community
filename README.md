# django-mvp-community

[![Tests](https://github.com/django-mvp/django-mvp-community/actions/workflows/tests.yml/badge.svg)](https://github.com/django-mvp/django-mvp-community/actions/workflows/tests.yml)
[![Build](https://github.com/django-mvp/django-mvp-community/actions/workflows/build.yml/badge.svg)](https://github.com/django-mvp/django-mvp-community/actions/workflows/build.yml)
[![Publish](https://github.com/django-mvp/django-mvp-community/actions/workflows/publish.yml/badge.svg)](https://github.com/django-mvp/django-mvp-community/actions/workflows/publish.yml)
[![codecov](https://codecov.io/gh/django-mvp/django-mvp-community/branch/main/graph/badge.svg)](https://codecov.io/gh/django-mvp/django-mvp-community)
[![PyPI](https://img.shields.io/pypi/v/django-mvp-community)](https://pypi.org/project/django-mvp-community/)
[![Development status](https://img.shields.io/pypi/status/django-mvp-community)](https://pypi.org/project/django-mvp-community/)
[![Python](https://img.shields.io/pypi/pyversions/django-mvp-community)](https://pypi.org/project/django-mvp-community/)
[![Django](https://img.shields.io/pypi/djversions/django-mvp-community)](https://pypi.org/project/django-mvp-community/)
[![License](https://img.shields.io/github/license/django-mvp/django-mvp-community)](https://github.com/django-mvp/django-mvp-community/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Notifications, mail and activity pages for django-mvp projects, built on established Django packages

<!--
  The README is this package's charter, and it is read in two places: on the
  repository page and on the package index. Write it for someone deciding
  whether to install this, who has not read anything else here.

  Every link is absolute. A relative link resolves on GitHub and 404s on PyPI,
  which is where the person deciding is most likely to be standing.

  The badge row above is the standard set for a published package: one status
  badge per workflow that runs on a push or a pull request, then coverage, the
  PyPI version, supported Python and Django, and the licence. A workflow added
  later gets its badge in the same row. The PyPI badges read "not found" until
  the first release, and the GitHub ones need the repository to be public.

  Sections, in this order:
    1. One sentence, above. What it does, for whom.
    2. Scope & philosophy — below. What it is and is not, and the principles
       that settle a close call.
    3. Installation.
    4. Quickstart — the smallest thing that works, end to end.
    5. The public surface, in full. For a package this small, list it.
    6. Anything genuinely surprising: what it deliberately does not do, what it
       leaves to the host project, and the failure modes that are quiet.

  Keep the CHANGELOG out of it. Link to it instead.
-->

## Scope & philosophy

django-mvp-community gives a django-mvp project the pages and components for
keeping people in touch with the site and with each other: notifications and
their preferences, push and reminders, email, and activity feeds. Each is built
on an established Django package, and this package supplies what those packages
leave to you: templates that match the rest of the application, menu entries,
Account Center pages, settings, and the few lines of wiring that connect one
package to another. Each feature is an optional extra, installed only when a
project wants it.

What it deliberately is not:

- **A notification, mail or activity engine.** It adds no logic or models of its
  own. The packages it builds on do the work.
- **Real-time.** No websockets or server-sent events. Unread counts refresh by
  polling.
- **Native phone push.** Web push to browsers and installed web apps only.
- **A mail service.** Mail goes out through whichever provider django-anymail is
  configured for.
- **A forum.**

When two designs conflict, the one with less code of our own wins. A template
override beats a Python hook, and an existing package beats anything written
here.

## Installation

```bash
pip install django-mvp-community
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "mvp_community",
]
```

This package requires [django-mvp](https://github.com/django-mvp/django-mvp).
It renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies, so it does nothing useful on its own.

## Quickstart

<!--
  The smallest complete example: what goes in the view, what goes in the
  template, and what appears on the page. Real code that runs, not a sketch.
  If the example needs three files, show three files.
-->

## Public surface

<!--
  Everything a host project can touch: components and their attributes,
  settings, template tags, models, views. Being able to list it exhaustively is
  a feature of a package this size, and the list is what makes an addition to
  it a deliberate decision rather than a side effect.
-->

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-community/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-community/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-community/blob/main/LICENSE).
