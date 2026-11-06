# ADR 0001 — Extras ship configurable views, and build in only their Account Center pages

**Status:** accepted

## Decision

A page whose content or address a host project could reasonably want to choose is shipped as a configurable view the host mounts itself, with its options as class attributes or `as_view()` arguments, and with no route or menu entry of the package's own. The activity extra's `ActivityFeedView` is the first: it is set to show what the signed-in person follows, the whole site, or one object, optionally limited to one kind of activity.

A page with nothing a host project would change is built in, with its route and its menu entry. Account Center pages are the case: the activity extra's following page, and the notifications extra's preferences page.

## Why

Where a feed lives, what it shows and what it is called differ between projects. Mounting one fixed feed page would have forced the package to choose for every project, and every project wanting something else would have had to work around it. A configured view is the way Django itself ships such pages (`LoginView`, `ListView`), costs a project one URL pattern and one menu entry, and leaves nothing to undo. Account Center pages are reached from the Account Center's own menu and card, so there is nothing for a project to place or name.

## Revisit if

Most projects end up mounting the same view with the same options at the same address, which would make a built-in page with an opt-out the cheaper default.
