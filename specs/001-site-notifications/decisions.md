# Decisions: Notifications on the site

## D1 — What "no further configuration" means

**Decision:** FR-002 and SC-001 mean no settings of this package's own. A host project still lists the extra's apps in `INSTALLED_APPS`, places the bell in `MVP_CONFIG["layout"]["navbar"]["end"]` and maps the two icon names, because django-mvp places every header widget and every icon that way.
**Why:** the package cannot add itself to another project's settings, and django-mvp's own widgets are placed the same way.
**Revisit if:** django-mvp gains a way for an installed app to contribute a header widget.
**ADR:** none — follows django-mvp's documented placement, nothing new to record.

## D2 — The unread count comes from a template tag

**Decision:** a tag library in `mvp_community/templatetags/` that imports the extra only inside the tag.
**Why:** a context processor would be one more setting for the host, and Django only finds tag libraries under an app's `templatetags/`. Importing inside the tag keeps the base install clean, which the existing base-install test proves.
**Revisit if:** the extras get apps of their own.
**ADR:** none — local to this extra.

## D3 — Preferences sit under account-center/

**Decision:** `account-center/notifications/`.
**Why:** Sam's ruling at the sketch gate: pages that belong to the Account Center sit behind `account-center/`.
**ADR:** none — a route, recorded in the spec and the docs.
