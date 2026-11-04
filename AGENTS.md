# AGENTS.md — Agent configuration for django-mvp-community

Notifications, mail and activity pages for django-mvp projects, built on established Django packages

Each extra is built on established Django packages: notifications, push
and reminders on django-generic-notifications, django-push-notifications and
django-celery-beat, mail on django-post-office and django-anymail, activity on
django-activity-stream, and share cards on Playwright. This package supplies the
templates, components, menu entries, Account Center pages and settings around
them, plus the few helpers that connect one package to another.

No models, no logic of its own, no migrations. Code that imports an extra's
packages lives in that extra's integration module and nowhere else, so the base
install imports nothing it may not have. Most changes here are templates.

## Stack and commands

- **Stack:** Python 3.12+ / Django 5.2, 6.0 and 6.1, uv-managed (hatchling build backend), built on
  django-mvp and django-cotton
- **Install:** `uv sync`
- **Test (whole suite):** `uv run pytest -n auto --dist loadscope`
- **Test (one class or file, while iterating):** `uv run pytest <path> -x` —
  serial, because starting the workers costs more than a focused run takes
- **Lint:** `uv run pre-commit run --all-files`
- **Type-check:** `uv run mypy`
- **Build:** `uv build`
- **Demo project:** `uv run python manage.py runserver 0.0.0.0:8000`
- **Bump the version:** `uv version` — never edit `pyproject.toml` alone, because `uv.lock`
  records this package's own version too

Lint is the pre-commit run rather than a bare `ruff check .`: the hook config
excludes `docs/` and migrations, so a raw invocation reports findings in paths
the gate does not cover, and they cannot be fixed without breaking the ones it
does.

`pre-commit run --all-files` only sees files git knows about. A new file that
has not been added is skipped, and the hooks then reformat it after the commit
that introduced it.

## The demo project

`demo/` is a Django project running on django-mvp's application shell. It is
how this package is looked at while it is being written, and it is never
deployed. Nothing in it is distributed — `pyproject.toml` packages
`mvp_community` alone.

`tests/settings.py` inherits `demo/settings.py` rather than restating it, so
there is one description of the shell.

Everything in the demo fails quietly. A Cotton component that cannot be
resolved renders as empty output, a Tailwind class the packaged stylesheet does
not emit does nothing, and a menu entry whose URL will not resolve is dropped
from the tree. None of them raise, which is why `tests/test_demo.py` asserts
against the rendered page rather than against the objects behind it.

**Adding a page** takes four things: a view in `demo/views.py` on
`mvp.views.MVPTemplateView`, a route in `demo/urls.py`, a template extending
`page_view.html` and filling `{% block page.content %}`,
and a `MenuItem` in `demo/menus.py`.

**Signing in.** `uv run python manage.py seed_demo` creates three accounts —
`regular.user@example.com`, `staff.user@example.com` and
`super.user@example.com`, all with the password `password`. The shell renders
differently for each, so all three exist rather than one. The command refuses
to run unless `DEBUG` is on.

## Components

Components live at
`mvp_community/templates/cotton/mvp_community/<name>.html`.
Cotton maps a tag's first segment onto that directory, so
`<c-mvp_community.example>` resolves to
`cotton/mvp_community/example.html`.

The directory name is load-bearing and fails quietly: a component Cotton cannot
resolve renders as empty output rather than raising, so renaming the directory
breaks every tag in it without an error anywhere. `tests/test_smoke.py`
asserts the directory exists for that reason.

## Releasing

Releases run through the shared release flow, never by hand and never by
pushing a tag.

1. Dispatch **Prepare Release** with a bump level. It opens a pull request
   carrying the version bump and the CHANGELOG section.
2. Merging that pull request is the release decision. **Tag Release** then cuts
   the tag and the GitHub Release from the merge commit.
3. **Publish** uploads to PyPI through trusted publishing. PyPI binds its
   trusted publisher to the `publish.yml` filename — renaming that file breaks
   publishing until the PyPI project settings are changed to match.

`pyproject.toml` holds the version and is the single source of truth for all
three steps.

**Tag Release skips a version with no matching CHANGELOG section**, which is
what stops the seed version being cut as a release. Leave it under
`## [Unreleased]` until Prepare Release promotes it: writing a `## [0.0.1]`
heading by hand makes the next push to `pyproject.toml` tag and release it.

Two things are needed before the first release: a PyPI trusted publisher for
this project pointed at `publish.yml`, and a `RELEASE_TOKEN` secret that can
write to this repository.

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

One `CONTEXT.md` at the repository root and `docs/adr/` for decisions.
See `docs/agents/domain.md`.

### CI checks

CI runs from the shared reusable workflows in `django-mvp/shared`, pinned at
`v0.6.0`. Because they are called rather than inlined,
their status checks carry the calling job as a prefix. The required checks are:

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.12, Django 6.0`
- `call-tests / Test Python 3.13, Django 5.2`
- `call-tests / Test Python 3.13, Django 6.0`
- `call-tests / Test Python 3.12, Django 6.1`
- `call-tests / Test Python 3.13, Django 6.1`

`tests.yml` and `build.yml` deliberately carry no `paths:` filter on
`pull_request`. A required check that is filtered out never reports, and a
check that never reports blocks the merge.

## Working here

Standards and the quality bar live in `CONSTITUTION.md`. The vocabulary to use
in issues, commits and test names lives in `CONTEXT.md`. What the package is
trying to be good at lives in `GOALS.md`, and the order the work happens in
lives in `docs/ROADMAP.md`.
