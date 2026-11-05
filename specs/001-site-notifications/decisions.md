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
**Why:** Sam's ruling at the sketch gate: pages that belong to the Account Center sit behind `account-center/`. django-mvp's own Account Center landing page is at `account/` in the demo, and the projects built on it mount it under `account-center/` themselves, so this page is where those projects put the rest of their Account Center.
**ADR:** none — a route, recorded in the spec and the docs.

## D4 — Saving preferences clears digest-frequency choices

**Decision:** known limitation, left as it is. `save_notification_preferences` deletes every digest-frequency choice and re-saves only the ones posted, and this page posts none.
**Why:** digests arrive with a later feature, which adds the frequency choice to this page. Until then no person can have one.
**Revisit if:** the digest feature is specified. It must post the frequency fields.
**ADR:** none — a watch item for the digest feature.

## D5 — Type and channel names come untranslated

**Decision:** the preferences page shows the names django-generic-notifications and the host project give, and the documentation says so.
**Why:** the names belong to the package and the project, not to this one.
**ADR:** none — local to the preferences page; the names belong to django-generic-notifications and the host project.

## D6 — The bell's refresh answers a signed-out request with 204

**Decision:** no redirect from the bell's refresh route.
**Why:** htmx follows a redirect and would swap the sign-in page into the header. The spec keeps the last count when a refresh fails.
**ADR:** none — local to one route; recorded in the developer guide.

## D7 — The notifications page lands with its mark-all-read route and the icons it names

**Decision:** the commit for the notifications page also carries the mark-all-read route and view and the two icon names, which the task list gave to later tasks.
**Why:** the approved list template links to the mark-all-read route and draws the preferences icon, and a template that names a route or icon that does not exist raises. The page could not render a populated list without them. The mark-all-read tests were written and seen failing before the view existed, and are committed with that task.
**Revisit if:** the list template stops naming either.
**ADR:** none — local to the order this feature's tasks were built in.
