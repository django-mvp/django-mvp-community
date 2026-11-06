# Decisions: Activity feeds and following

## D1 — The following page shows no activity

**Decision:** the following page in the Account Center manages what a person follows and shows no activity. Activity is shown by a feed the host project mounts (D7) and by recent activity.
**Why:** Sam confirmed the reading at intake: managing follows and reading activity are separate jobs.
**ADR:** none — recorded in the spec.

## D2 — Only public activity reaches a feed

**Decision:** every feed shows only activity the host project recorded as public. Hiding activity about an object from people who may not see it stays with the host project.
**Why:** the package adds no logic of its own (Article XII), and recording activity, public or not, is the host project's job. django-activity-stream marks each activity public or not.
**Revisit if:** a host project needs feeds filtered by object permissions.
**ADR:** none — follows the package's scope.

## D3 — Recent activity joins the glossary

**Decision:** CONTEXT.md gains **recent activity**, the newest few activities placed on any page, in the pull request that builds the feature. A **feed** stays the paged list on a page of its own.
**Why:** Sam, at the sketch gate: a feed dedicated to a page and a few activities dropped into a dashboard are different things and need different words. Without one the second drifts towards "stream" or "widget", which the glossary avoids.
**ADR:** none — a glossary change.

## D4 — Only django-activity-stream's follow routes are mounted

**Decision:** the package's URLconf carries django-activity-stream's four follow patterns, taken by name from `actstream.urls`, and nothing else of it. A host adds one include.
**Why:** the design review showed `actstream.urls` also mounts `detail/<id>/`, which shows actions that are not public to anyone, and `following/<user_id>/`, which shows anyone's follows. Mounting only what the feature uses closes both and meets SC-001's one include.
**ADR:** none — local to this extra's URLconf.

## D5 — The follow control's refresh route stays, signed-in only

**Decision:** `FollowControlView` stays, as agreed at the sketch gate, behind `LoginRequiredMixin`, answering 404 for a model not registered with django-activity-stream. The review's alternative (htmx selecting the control out of a full page) was not adopted.
**Why:** that alternative re-renders the whole page per click, which is the cost the sketch-gate note set out to remove. Only a signed-in person ever reaches the route, after a follow they made.
**ADR:** none — local to one route.

## D6 — Following records "started following"

**Decision:** django-activity-stream's follow view is used as it is, so following records a public "started following" activity. The feed page leaves out the person's own actions.
**Why:** Sam, 2026-11-06, approving the spec change: stopping the activity would mean a follow view of our own. Excluding a person's own actions keeps their feed to what others did.
**ADR:** none — recorded in the spec.

## D7 — A feed is a view the host mounts, not a page the package ships

**Decision:** the package provides `ActivityFeedView`, an `MVPListView` configured with `stream` (`following`, `site`, `object`), `verb` and `get_stream_object()`, and mounts no feed page or menu entry. The following page stays built in, in the Account Center.
**Why:** Sam, 2026-11-06: a host project decides where a feed lives and what it shows, so the package should not choose for it. The Account Center pages have no configuration a host would change, so they stay built in. This also settles FR-008 for the feed page.
**Revisit if:** most host projects end up mounting the same following feed at the same address.
**ADR:** docs/adr/0001-extras-ship-configurable-views-and-built-in-account-center-pages.md

## D8 — The URLconf carries no app namespace of its own

**Decision:** `mvp_community.integrations.activity.urls` declares no `app_name`. Its own page is included inside it with the namespace `mvp_community_activity`, and django-activity-stream's four follow routes sit beside it with their own names, outside any namespace.
**Why:** django-activity-stream's `follow_url` and `follow_all_url` tags reverse `actstream_follow` and its siblings without a namespace. An `app_name` on the module would put those four names behind it and the tags would fail to resolve. The host still adds one include.
**Revisit if:** django-activity-stream's tags learn to reverse a namespaced route.
**ADR:** none — local to this extra's URLconf.

## D9 — A tag builds the follow control's refresh address

**Decision:** `follow_control_url obj next` joins `followers_of` in `mvp_community_activity`. It returns the address of the `follow_control` route for an object, carrying `next`. The route is drawn through a small page template, `mvp_community/activity/follow_control.html`, that places the `follow` component.
**Why:** the control's htmx post needs the content type's number to name the refresh route, and a template has no way to get it. Rendering a Cotton component directly would replace the variables the view passes with the component's defaults, so the view renders a template that places it.
**Revisit if:** django-activity-stream's tags learn to give a content type's number.
**ADR:** none — local to this extra.
