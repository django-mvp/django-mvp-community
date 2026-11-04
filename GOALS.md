# Goals

These are the standing directions `django-mvp-community` works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the package incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | A project's notifications look like the rest of its application: a bell with an unread count, a notifications page, and each person's notification preferences in the Account Center | Essential | | |
| G2 | Each feature is installed on its own, and a project never carries the packages of a feature it does not use | Essential | | |
| G3 | Any page or component can be changed by overriding one template, without forking the package | Essential | | |
| G4 | Email from the project matches its look, is translated, can be gathered into a digest, and can be unsubscribed from in one click | Essential | | |
| G5 | Notifications reach people by web push as well as on the site and by email, through the same preferences | Expected | | |
| G6 | People get reminders on a schedule they choose, in their own timezone | Expected | | |
| G7 | A project can show feeds of activity and let people follow other people and objects | Expected | | |
| G8 | A shared link to a page shows a generated preview image of it | Aspirational | | |
| G9 | People can comment on any page or object | Aspirational | | |

_Written 2026-11-04. Revise as the goals change._
