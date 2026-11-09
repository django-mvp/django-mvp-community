# Feature Specification: Notifications on the site

**Feature Branch**: `001-site-notifications`

**Created**: 2026-11-05

**Status**: Draft

**Serves**: G1, a project's notifications look like the rest of its application, with a bell and
an unread count, a notifications page, and each person's notification preferences in the Account
Center. G3, each of those pages and components can be changed by overriding one template.

**Roadmap**: R3, notifications on the site

**Issue**: #7

**Input**: People using a site built on django-mvp see what happened to them without leaving the
application: a bell in the shell with their unread count, kept current without reloading the page,
a notifications page listing what they received with the newest first, a way to mark everything
read, and a page in the Account Center where they turn each notification type and each channel on
or off. A host project gets all of this by installing the notifications extra, and can change any
of these pages or components by overriding one template. Deciding when a notification is sent
stays with the host project. Notifications, notification types and preferences are those of
django-generic-notifications.

## Clarifications

### Session 2026-11-05

- Q: What does the bell's count include? → A: The person's unread notifications on the site, and
  nothing else. Notifications that reach a person only by another channel are not counted.
- Q: How is a notification with nothing to link to marked read? → A: By marking everything read.
  Opening a notification that links somewhere marks it read, and the feature offers no way to mark
  one notification read on its own.
- Q: What happens to notifications a person already received when they turn that type off on the
  site? → A: They stay on the notifications page. Turning a type off stops new ones from arriving
  on the site from then on, which is how the package the feature is built on behaves.
- Q: Which channels does the preferences page list? → A: Every channel the host project has
  installed. With this feature alone that is the site. A channel added later, such as email,
  appears on the same page without this feature changing.
- Q: Where does the preferences page live? → A: Under the Account Center's own address,
  `account/`, where pages that belong to the Account Center sit: `account/notifications/`.
- Q: What does a signed-out visitor see? → A: No bell. A signed-out visit to the notifications
  page or the preferences page is sent to sign in, as for every other Account Center page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer turns notifications on (Priority: P1)

A developer building a site on django-mvp installs the notifications extra and includes its URLs.
From then on, a signed-in person has a bell in the shell, a notifications page and a notification
preferences page in the Account Center, with no further configuration. The developer declares the
site's notification types and decides when each notification is sent. Where the developer wants a
page or a component to look or read differently, they override that one template.

**Why this priority**: Nothing else in the feature reaches anyone until a host project can switch
it on.

**Independent Test**: Install the extra in a project, include its URLs, sign in, and find the bell,
the notifications page and the preferences entry in the Account Center.

**Acceptance Scenarios**:

1. **Given** a project that has installed the notifications extra and included its URLs, **When**
   a person signs in, **Then** the shell shows the bell, and the Account Center has an entry and a
   card for notification preferences.
2. **Given** a project that has not installed the notifications extra, **When** any page renders,
   **Then** there is no bell, no notifications page and no preferences entry, and nothing that
   belongs to the extra is imported.
3. **Given** a project that overrides the template of one page or component of this feature,
   **When** that page or component renders, **Then** the project's template is used and every
   other part of the feature is unchanged.
4. **Given** a project that declares a notification type, **When** the preferences page renders,
   **Then** that type is listed.

---

### User Story 2 - A person sees and reads their notifications (Priority: P1)

A signed-in person sees from the bell how many unread notifications they have, on any page of the
site. When a new notification arrives, the count goes up without the page being reloaded. The bell
takes them to their notifications page, which lists what they received, newest first, with unread
ones set apart from read ones. Opening a notification that links somewhere takes them there and
marks it read. They can mark everything read at once.

**Why this priority**: Seeing what happened is the reason the package exists.

**Independent Test**: Send a person notifications, sign in as them, follow the bell to the
notifications page, open one, and mark the rest read.

**Acceptance Scenarios**:

1. **Given** a person with unread notifications, **When** any page in the shell renders, **Then**
   the bell shows how many are unread.
2. **Given** a person with no unread notifications, **When** any page in the shell renders,
   **Then** the bell shows no count.
3. **Given** a person on a page that is already open, **When** a new notification reaches them on
   the site, **Then** the bell's count rises without the page being reloaded.
4. **Given** a person with notifications, **When** they open the notifications page, **Then** it
   lists their notifications newest first and tells read from unread.
5. **Given** an unread notification that links somewhere, **When** the person opens it, **Then**
   they are taken where it links and it is marked read.
6. **Given** a person with unread notifications, **When** they mark everything read, **Then** none
   of their notifications is unread and the bell shows no count.
7. **Given** a person with no notifications, **When** they open the notifications page, **Then**
   the page says they have none.
8. **Given** a person with more notifications than one page holds, **When** they open the
   notifications page, **Then** the newest are shown and they can move on to older ones.
9. **Given** two people, **When** one opens the notifications page, **Then** they see only their
   own notifications.

---

### User Story 3 - A person chooses which notifications they receive (Priority: P2)

A signed-in person opens notification preferences in the Account Center and sees each notification
type the site declares, with each channel the site has installed. They turn each type on or off for
each channel and save. From then on they receive notifications only where they left them on.

**Why this priority**: The bell and the page are useful without it, but people who get too much
need a way to say so.

**Independent Test**: Sign in, open notification preferences, turn one type off on the site, send
that person a notification of that type, and see that it does not arrive on the site.

**Acceptance Scenarios**:

1. **Given** a signed-in person, **When** they open notification preferences, **Then** every
   notification type the site declares is listed against every installed channel, showing the
   person's current choice for each.
2. **Given** a person who turns a type off on the site and saves, **When** a notification of that
   type is sent to them, **Then** it does not appear on their notifications page and does not add
   to the bell's count.
3. **Given** a person who turns a type off and saves, **When** they open the preferences page
   again, **Then** that type is shown off and every other choice is as they left it.
4. **Given** a person who turns a type off on the site, **When** they open the notifications page,
   **Then** notifications of that type they already received are still listed.

---

### Edge Cases

- A signed-out visitor sees no bell, and is sent to sign in from the notifications and preferences
  pages.
- A notification whose link no longer resolves is still listed, and opening it still marks it read.
- A link to a notification the person does not have, because it was deleted after a push carried
  the link or because it is someone else's, opens their notifications page and changes nothing.
- The bell's refresh fails, for example because the person signed out in another tab: the page
  keeps working and the bell keeps its last count.
- A site that declares no notification types shows a preferences page saying there is nothing to
  choose.
- A notification type a site stops declaring is no longer listed on the preferences page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Installing the notifications extra MUST bring the package the feature is built on,
  and installing the package without it MUST import nothing that belongs to it.
- **FR-002**: A host project MUST be able to switch the feature on by installing the extra,
  listing its apps, including its URLs and placing the bell in the header, with no settings of
  the package's own.
- **FR-003**: The shell MUST show a bell to every signed-in person, with the number of their
  unread notifications on the site, and no count when there are none.
- **FR-004**: The bell's count MUST be kept current on an open page without a reload, by polling.
- **FR-005**: The bell MUST lead to the notifications page.
- **FR-006**: The notifications page MUST list only the signed-in person's own notifications,
  newest first, telling read from unread, split into pages when there are more than one page holds.
- **FR-007**: Opening a notification that links somewhere MUST take the person there and mark it
  read.
- **FR-008**: A person MUST be able to mark all their notifications read in one action.
- **FR-009**: The Account Center MUST have an entry and a card for notification preferences.
- **FR-010**: The preferences page MUST list every notification type the site declares against
  every installed channel, and let the person turn each one on or off and save.
- **FR-011**: A saved preference MUST decide whether later notifications of that type reach the
  person on that channel, and MUST NOT remove notifications already received.
- **FR-012**: Every page and component of the feature MUST be replaceable by overriding one
  template.
- **FR-013**: The notifications page and the preferences page MUST require a signed-in person.
- **FR-014**: Every string the feature shows MUST be translatable.

### Traceability

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-009, FR-012, FR-014 |
| US2 | FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-013 |
| US3 | FR-010, FR-011, FR-013 |

### Key Entities

- **Notification**: one message to one person about something that happened, read or unread, which
  may link to what it is about. Owned by django-generic-notifications.
- **Notification type**: a kind of notification the host project declares. Owned by
  django-generic-notifications.
- **Channel**: a way a notification reaches a person. This feature presents the site channel, and
  lists any other the project has installed.
- **Notification preferences**: a person's choice, per notification type and channel, of whether
  to receive it. Owned by django-generic-notifications.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer switches the feature on in an existing django-mvp project by installing
  the extra, listing its apps, adding one URL include and naming the bell in the header, with no
  settings of the package's own.
- **SC-002**: A notification sent to a person with a page open shows in the bell's count within
  one minute, without a reload.
- **SC-003**: From any page, a person reaches their newest notification in two actions: the bell,
  then the notification.
- **SC-004**: A person changes one preference in three actions or fewer from the Account Center.
- **SC-005**: Each page and component is replaced by overriding exactly one template, with no
  Python change.

## Assumptions

- django-generic-notifications provides the notifications, notification types, channels and
  preferences, and this package adds no models of its own.
- The Account Center, its menu and its card block are django-mvp's own, and this feature adds to
  them the way django-mvp-accounts does.
- The host project decides when a notification is sent and to whom.
- Email as a channel and digests arrive with a later feature, and their choices join the same
  preferences page.
- The bell has no dropdown. It leads to the notifications page.
