# Feature Specification: Activity feeds and following

**Feature Branch**: `002-activity-feeds-and-following`

**Created**: 2026-11-05

**Status**: Draft

**Serves**: G7, a project can show feeds of activity and let people follow other people and
objects. G3, each page and component of the feature can be changed by overriding one template.

**Roadmap**: R7, activity feeds and following

**Issue**: #12

**Input**: People using a site built on django-mvp keep up with the people and things they care
about without going looking for them. Next to a person or an object they find a control to follow
it or stop following it, showing how many people follow it, and a feed page shows what the people
and things they follow have been doing, newest first. A "following" page in the Account Center
lists everything they follow and lets them stop following any of it. A host project can also show
what happened across the project, or around one object, as a feed on any page it chooses, limit a
feed to some kinds of activity, and show who follows a person or an object. All of this comes with
the activity extra, and any page or component can be changed by overriding one template. What
counts as activity, and when it is recorded, stays with the host project. Activity and follows are
those of django-activity-stream.

## Clarifications

### Session 2026-11-05

- Q: Where does a person see the activity of what they follow? → A: On a feed page of the
  feature's own, in the application shell and reachable from the menu. The following page in the
  Account Center manages what they follow and does not show the feed.
- Q: Which activity does a feed show? → A: Only activity the host project recorded as public.
  Keeping activity about an object from people who may not see that object stays with the host
  project, which decides what it records as public.
- Q: What does a signed-out visitor see? → A: A project feed or an object feed the host project
  placed on a public page, and the follow control with its count. Using the follow control sends
  them to sign in. The feed page and the following page send them to sign in, as every other
  Account Center page does.
- Q: Can a person follow themselves? → A: No. The follow control is not offered to a person on
  themselves, and their own activity is not added to their feed by following.
- Q: What does a follower count count? → A: The people following that person or object. A
  person's own follow is included, and the count changes as soon as they follow or stop
  following.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer turns activity on and places feeds and follow controls (Priority: P1)

A developer building a site on django-mvp installs the activity extra and includes its URLs. From
then on a signed-in person has a feed page and a following page in the Account Center, with no
further configuration. The developer records activity where their site decides something happened,
and places the feature's components on their own pages: a follow control next to a person or an
object, a project feed showing everything that happened on the site, an object feed showing what
happened around one object, and a list of the people following a person or an object. Any feed can
be limited to some kinds of activity. Where the developer wants a page or a component to look or
read differently, they override that one template.

**Why this priority**: Nothing else in the feature reaches anyone until a host project can switch
it on and place it.

**Independent Test**: Install the extra in a project, include its URLs, record some activity, place
a project feed, an object feed, a follow control and a followers list on pages of the project, and
find each of them, the feed page and the following page.

**Acceptance Scenarios**:

1. **Given** a project that has installed the activity extra and included its URLs, **When** a
   person signs in, **Then** the menu leads to their feed page, and the Account Center has an entry
   and a card for the following page.
2. **Given** a project that has not installed the activity extra, **When** any page renders,
   **Then** there is no feed page, no following page and no entry for either, and nothing that
   belongs to the extra is imported.
3. **Given** a project feed placed on a page, **When** the page renders, **Then** it lists the
   public activity recorded across the site, newest first.
4. **Given** an object feed placed for one object, **When** the page renders, **Then** it lists the
   public activity in which that object is the one who acted, the one acted on or the one it
   happened in, and no other activity.
5. **Given** a feed limited to some kinds of activity, **When** it renders, **Then** it lists
   activity of those kinds only.
6. **Given** a follow control placed for a person or an object, **When** the page renders, **Then**
   it shows how many people follow them.
7. **Given** a followers list placed for a person or an object, **When** the page renders, **Then**
   it lists the people who follow them.
8. **Given** a project that overrides the template of one page or component of this feature,
   **When** that page or component renders, **Then** the project's template is used and every
   other part of the feature is unchanged.

---

### User Story 2 - A person follows people and things and sees their activity (Priority: P1)

A signed-in person finds a follow control next to a person or an object, showing how many people
follow it. They follow it, and the count includes them. From then on their feed page shows what
the people and things they follow have been doing, newest first. They stop following with the same
control, and that activity no longer reaches their feed.

**Why this priority**: Following and seeing what happened is the reason the feature exists.

**Independent Test**: Sign in, follow a person and an object, record activity by the person and
about the object, and find both on the feed page. Stop following the person and see their new
activity no longer arrive.

**Acceptance Scenarios**:

1. **Given** a signed-in person who does not follow a person or an object, **When** they use its
   follow control, **Then** they follow it, the control shows that they do, and its count rises
   by one.
2. **Given** a signed-in person who follows a person or an object, **When** they use its follow
   control, **Then** they no longer follow it, the control shows that they do not, and its count
   falls by one.
3. **Given** a person who follows another person and an object, **When** they open their feed
   page, **Then** it lists the public activity of both, newest first, and no activity of anyone or
   anything they do not follow.
4. **Given** a person who stops following someone, **When** that someone does something new,
   **Then** it does not appear on the person's feed page.
5. **Given** a person who follows nothing, **When** they open their feed page, **Then** the page
   says there is nothing yet and points them to following people and things.
6. **Given** a person whose feed holds more activity than one page holds, **When** they open their
   feed page, **Then** the newest is shown and they can move on to older activity.
7. **Given** a signed-out visitor, **When** they use a follow control, **Then** they are sent to
   sign in.
8. **Given** a signed-in person, **When** a follow control for themselves renders, **Then** it does
   not offer to follow.

---

### User Story 3 - A person reviews and trims what they follow (Priority: P2)

A signed-in person opens the following page in the Account Center and sees every person and object
they follow. They stop following any of them from that page.

**Why this priority**: Following and the feed are useful without it, but someone who follows a lot
needs one place to see it all and cut it back.

**Independent Test**: Sign in, follow two people and an object, open the following page, stop
following one person, and see them gone from the list and their new activity gone from the feed.

**Acceptance Scenarios**:

1. **Given** a person who follows people and objects, **When** they open the following page,
   **Then** it lists everything they follow, each leading to its page where it has one.
2. **Given** a person on the following page, **When** they stop following one entry, **Then** it
   leaves the list, it no longer counts them, and its new activity no longer reaches their feed.
3. **Given** a person who follows nothing, **When** they open the following page, **Then** the page
   says they follow nothing.
4. **Given** a person who follows more than one page holds, **When** they open the following page,
   **Then** the first page is shown and they can move on to the rest.

---

### Edge Cases

- A signed-out visitor is sent to sign in from the feed page and the following page.
- A person or object someone follows is deleted: it drops off their following page, its count is
  gone with it, and their feed carries on without it.
- Activity about an object that has since been deleted stays out of every feed rather than showing
  a broken entry.
- Activity the host project recorded as not public appears in no feed.
- A project feed or an object feed with no activity says there is nothing yet.
- Two people following the same object at once both end up following it, and its count includes
  both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Installing the activity extra MUST bring the package the feature is built on, and
  installing the package without it MUST import nothing that belongs to it.
- **FR-002**: A host project MUST be able to switch the feature on by installing the extra, listing
  its apps and including its URLs, with no settings of the package's own.
- **FR-003**: The feature MUST provide a follow control for any person or object, which a
  signed-in person uses to follow or stop following it and which shows how many people follow it.
- **FR-004**: The follow control MUST send a signed-out visitor to sign in, and MUST NOT offer a
  person to follow themselves.
- **FR-005**: The feature MUST provide a feed page listing the public activity of the people and
  objects the signed-in person follows, newest first.
- **FR-006**: The feature MUST provide a project feed component listing the public activity
  recorded across the site, newest first.
- **FR-007**: The feature MUST provide an object feed component listing the public activity in
  which one given object acted, was acted on, or was where it happened, newest first.
- **FR-008**: A host project MUST be able to limit any feed to some kinds of activity.
- **FR-009**: The feature MUST provide a followers list component listing the people who follow a
  given person or object.
- **FR-010**: The Account Center MUST have an entry and a card for a following page, which lists
  everything the signed-in person follows and lets them stop following each one.
- **FR-011**: Feeds MUST NOT show activity that is not public, or activity about an object that no
  longer exists.
- **FR-012**: Every feed and list MUST be split into pages when it holds more than one page.
- **FR-013**: The feed page and the following page MUST require a signed-in person.
- **FR-014**: Every page and component of the feature MUST be replaceable by overriding one
  template.
- **FR-015**: Every string the feature shows MUST be translatable.

### Traceability

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-006, FR-007, FR-008, FR-009, FR-011, FR-012, FR-014, FR-015 |
| US2 | FR-003, FR-004, FR-005, FR-011, FR-012, FR-013 |
| US3 | FR-010, FR-012, FR-013 |

### Key Entities

- **Activity**: a record that someone did something to something, possibly in the context of
  something else, public or not. Recorded by the host project, owned by django-activity-stream.
- **Follow**: a person's choice to see activity about another person or an object. Owned by
  django-activity-stream.
- **Feed**: the list of activity a person sees, drawn from what they follow.
- **Project feed**: the list of all public activity recorded across the site.
- **Object feed**: the list of public activity around one object.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer switches the feature on in an existing django-mvp project by installing
  the extra, listing its apps and adding one URL include, with no settings of the package's own.
- **SC-002**: A developer places a follow control, a project feed, an object feed or a followers
  list on a page with one component tag each.
- **SC-003**: A person follows or stops following something in one action, and sees the change on
  the control without leaving the page.
- **SC-004**: From any page, a person reaches the newest activity of what they follow in one
  action from the menu.
- **SC-005**: Each page and component is replaced by overriding exactly one template, with no
  Python change.

## Assumptions

- django-activity-stream provides activity, follows and the queries behind every feed, and this
  package adds no models of its own.
- The host project records activity and decides what is public. Nothing in this feature records
  activity on its own.
- The Account Center, its menu and its card block are django-mvp's own, and this feature adds to
  them the way the notifications feature does.
- Telling people about new activity in their notifications, by email or by push is not part of this
  feature.
- Feeds refresh when the page loads. Nothing updates them on an open page.
