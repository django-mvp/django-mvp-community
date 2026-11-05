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

## D3 — Project feed and object feed join the glossary

**Decision:** CONTEXT.md gains **project feed** and **object feed** in the pull request that builds the feature.
**Why:** the spec names both, and without a defined word they drift towards "stream" and "timeline", which the glossary already avoids.
**ADR:** none — a glossary change.
