# Decisions: Activity feeds and following

## D1 — The feed page is the feature's own

**Decision:** a person's feed is a page in the application shell, reached from the menu. The following page in the Account Center manages follows and shows no activity.
**Why:** Sam confirmed the reading at intake: the feature ships a feed page of its own, and the components let a host project put feeds elsewhere too.
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
