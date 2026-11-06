# Feature Specification: Notifications by email, and digests

**Feature Branch**: `004-notifications-by-email`

**Created**: 2026-11-06

**Status**: Draft

**Serves**: G1, a project's notifications look like the rest of its application, with each
person's notification preferences in the Account Center. G4, email from the project matches its
look, is translated, can be gathered into a digest, and can be unsubscribed from in one click. This
feature delivers the digest and the unsubscribe, which completes G4.

**Roadmap**: R4, notifications by email, and digests

**Issue**: #23

**Input**: People who use a site built on django-mvp should be able to get their notifications by
email as well as on the site. Email becomes one more channel on the notification preferences page
in the Account Center, so a person turns each notification type on or off for email the same way
they already do for the site. Someone who doesn't want an email for every notification can choose
a daily or weekly digest that gathers them into one email. Every notification and digest email has
a one-click unsubscribe, so a person can stop that email from the email itself without signing in.
The emails go through the mail extra, so they are queued, logged, translated and laid out like the
rest of the project's email. Deciding when a notification is sent stays with the host project.
Push and reminders are not part of this.

## Clarifications

### Session 2026-11-06

- Q: Is how often email comes chosen once, or per notification type? → A: Per notification type.
  A person can have one email per notification for replies and a weekly digest for everything
  else.
- Q: What does an unsubscribe in a notification email turn off? → A: Email for that notification
  type only. The person keeps receiving that type on the site, and keeps receiving other types by
  email.
- Q: What does an unsubscribe in a digest turn off? → A: Email for every notification type that
  digest gathered. The site channel is never changed by an unsubscribe.
- Q: What does one-click mean? → A: The standard unsubscribe header that mail apps show as an
  "Unsubscribe" button beside the sender, which unsubscribes without the person opening any page.
  The link in the email opens a page with one button that turns the email off, signed in or not.
  Following the link alone changes nothing, because mail security scanners open every link in an
  email before the person sees it (Sam, 2026-11-06).
- Q: Can every notification type be gathered into a digest? → A: No. A type the host project
  always sends on some channel, such as system messages and security notices, is always emailed
  as it happens, and the preferences page offers no choice of how often for it (Sam, 2026-11-06).
- Q: Does the package send digests on a schedule? → A: No. The package sends the digests that are
  due when it is asked to. The documentation explains how a host project runs that daily and
  weekly, as it does for sending the mail queue.
- Q: What happens with only the notifications extra installed? → A: Nothing changes. The
  preferences page shows the site channel alone, as it does today, and no email is sent.
- Q: What does a digest contain? → A: The notifications of the types the person chose for that
  digest that arrived since their last digest and that they have not already read on the site. A
  digest with nothing in it is not sent.
- Q: Where does the unsubscribe link lead? → A: To a page that names the email it will turn off,
  with a button that turns it off and a link to the full notification preferences. Once turned off,
  the page says what was turned off. It works for a person who is not signed in.
- Q: In which language are notification and digest emails written? → A: The recipient's.
- Q: Does a person see notification types the host project never declared? → A: No.
  django-generic-notifications registers a "System Message" type of its own, in English only, with
  email always on. The notifications extra removes it, so the preferences page lists only the
  types the host project declares (Sam, 2026-11-06).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer sends notifications by email (Priority: P1)

A developer whose project already uses the notifications extra installs the mail extra beside it
and follows the documented settings. Email then appears as a channel on every person's
notification preferences page, and each notification a person has left on for email reaches them
as an email, queued and logged like the rest of the project's email and laid out in django-mvp's
email layout. The developer arranges for digests to be sent daily and weekly as the documentation
describes, and can change how any notification or digest email looks by overriding one template.

**Why this priority**: No person can receive a notification by email, as it happens or in a
digest, until a project can send them.

**Independent Test**: In a project with both extras installed, send a notification to a person who
has email on for its type, then find it queued and logged and read it in the project's email
layout. Install only the notifications extra and find the preferences page and sending unchanged.

**Acceptance Scenarios**:

1. **Given** a project with the notifications and mail extras installed and configured, **When** a
   person opens their notification preferences, **Then** email is listed as a channel beside the
   site.
2. **Given** a person who has email on for a notification type and receives each one as it
   happens, **When** the project sends them a notification of that type, **Then** an email about it
   is queued and logged, addressed to them, in their language and in django-mvp's email layout.
3. **Given** a person who has email off for a notification type, **When** the project sends them a
   notification of that type, **Then** no email is sent and the notification still appears on the
   site if they have the site on.
4. **Given** a person with no email address, **When** the project sends them a notification,
   **Then** no email is sent and nothing fails.
5. **Given** people who chose a daily or a weekly digest, **When** the project sends the digests
   that are due, **Then** each of them who has unread notifications for that digest receives one
   email gathering them, and nobody else receives one.
6. **Given** a project that installs only the notifications extra, **When** a person opens their
   notification preferences and receives notifications, **Then** the site is the only channel
   listed and no email is sent.
7. **Given** a project that overrides a notification or digest email's template, **When** that
   email is sent, **Then** it uses the project's template.

---

### User Story 2 - A person chooses how often notification email comes (Priority: P1)

A person who gets too much email opens their notification preferences in the Account Center. For
each notification type they have on for email, they choose whether it comes as one email each time,
in a daily digest, or in a weekly digest, and save. Types the site always sends, such as security
notices, always arrive as they happen. From then on that type reaches their inbox the
way they chose, and their choices for the site are unchanged.

**Why this priority**: Without it, a person's only choice is an email for every notification or
none, which is the reason people turn notification email off altogether.

**Independent Test**: Choose a weekly digest for one notification type and one email each time for
another, receive notifications of both, and find one email straight away for the second and the
first gathered into the next weekly digest.

**Acceptance Scenarios**:

1. **Given** a person on their notification preferences page, **When** they look at a notification
   type, **Then** they see how often its email comes, with one email each time, a daily digest and
   a weekly digest to choose from.
2. **Given** a person who chooses a daily digest for a type and saves, **When** notifications of
   that type arrive, **Then** no email is sent for each one, and they are gathered into the next
   daily digest.
3. **Given** a person who switches a type from a digest back to one email each time, **When** the
   next notification of that type arrives, **Then** it is emailed straight away.
4. **Given** a person who read a notification on the site before their digest was due, **When** the
   digest is sent, **Then** that notification is left out of it.
5. **Given** a person who has not chosen how often, **When** notifications arrive, **Then** each
   type follows the default the host project declared for it.
6. **Given** a notification type the host project always sends on some channel, **When** a person
   opens their preferences, **Then** it offers no choice of how often, and its email always
   arrives as it happens.
7. **Given** a person who turns email off for a type, **When** they look at that type, **Then** the
   choice of how often cannot be changed, and their earlier choice is kept for when they turn
   email back on.

---

### User Story 3 - A person unsubscribes from notification email in one click (Priority: P2)

A person reads a notification or a digest email they no longer want. They use the unsubscribe
button their mail app shows beside the sender, or follow the unsubscribe link at the bottom of the
email and press the one button on the page it opens. The email it came from stops, without them
signing in, and the page says what was turned off and how to change their other choices.

**Why this priority**: People can already turn notification email off in their preferences, so
this is the faster way out rather than the only one. It is also what mail providers expect of
email sent in bulk.

**Independent Test**: Receive a notification email while signed out, follow its unsubscribe link,
press the button, and find email off for that type alone on the preferences page. Do the same from a digest and find
email off for every type the digest gathered.

**Acceptance Scenarios**:

1. **Given** a notification email, **When** the person follows its unsubscribe link, signed in or
   not, **Then** the page names the email it will turn off and nothing is changed yet.
2. **Given** that page, **When** the person presses its button, **Then** email for that
   notification type is turned off for them and the page says so, with a link to their
   notification preferences.
3. **Given** a digest email, **When** the person confirms on the page its unsubscribe link opens,
   **Then** email for every notification type that digest gathered is turned off for them.
4. **Given** a notification or digest email, **When** the person's mail app unsubscribes through
   the email's unsubscribe header, **Then** the same email is turned off without the person opening
   any page.
5. **Given** an unsubscribe, **When** the person later receives notifications, **Then** their site
   notifications and their email for other types are unchanged.
6. **Given** an unsubscribe link that has been altered, or one belonging to another person,
   **When** it is followed, **Then** nothing is changed and the page says the link is not valid.
7. **Given** a person who already unsubscribed, **When** they follow the same link again, **Then**
   nothing fails and the page says that email is already off.
8. **Given** a person who unsubscribed, **When** they turn email back on in their preferences,
   **Then** the email resumes.

---

### Edge Cases

- A notification type the host project declares as always sent for email: its email has no
  unsubscribe link or header, and the preferences page shows it as always sent, as it does for the
  site today.
- The digests are not sent on the day they were due: the notifications wait and are gathered into
  the next digest that is sent, and none is lost or sent twice.
- A person's email address changes between a notification and their digest: the digest goes to the
  address they have when it is sent.
- A notification type is removed from the host project while it is waiting for a digest: it is left
  out of the digest.
- A person deletes their account: they receive no further digests, and their unsubscribe links do
  nothing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: With the notifications and mail extras both installed and the documented settings
  applied, email MUST be a channel on the notification preferences page and notifications MUST be
  sent by email to people who left it on.
- **FR-002**: With the notifications extra installed and the mail extra not, the preferences page
  MUST list the site channel only, and no notification MUST be sent by email.
- **FR-003**: A notification or digest email MUST be queued and logged like every other email the
  project sends, MUST be laid out in django-mvp's email layout, and MUST be written in the
  recipient's language.
- **FR-004**: A notification MUST NOT be emailed to a person who has email off for its type, or who
  has no email address.
- **FR-005**: For each notification type on for email, a person MUST be able to choose one email
  each time, a daily digest or a weekly digest, and the choice MUST apply to notifications of that
  type from then on. The choice MUST NOT be changeable for a type while its email is off, and MUST be kept.
- **FR-016**: A notification type the host project always sends on some channel MUST always be
  emailed as it happens, and MUST offer no choice of how often.
- **FR-017**: The preferences page MUST list only the notification types the host project
  declares, and none that a package registers on its own.
- **FR-006**: A person who has not chosen MUST receive each type at the frequency the host project
  declared as its default.
- **FR-007**: When the host project sends the digests that are due, each person MUST receive at most
  one email per digest, gathering the unread notifications of the types they chose for it that
  arrived since their last one. A digest with nothing in it MUST NOT be sent.
- **FR-008**: The package MUST NOT run anything that sends digests on a schedule. The host project
  MUST be able to send them daily and weekly as the documentation describes.
- **FR-009**: Every notification and digest email whose types a person can turn off MUST carry an
  unsubscribe link that works without signing in, and the standard unsubscribe header that lets a
  mail app unsubscribe in one click. Following the link MUST change nothing until the person
  confirms on the page it opens.
- **FR-010**: Unsubscribing from a notification email MUST turn off email for that notification
  type, and unsubscribing from a digest MUST turn off email for every type it gathered. Neither MUST
  change any other preference.
- **FR-011**: An unsubscribe link MUST change only the preferences of the person it was sent to,
  and MUST change nothing when it has been altered.
- **FR-012**: Following an unsubscribe link MUST open a page naming the email it will turn off with
  a button to confirm, or saying it was already off, or that the link is not valid, and after
  confirming MUST say what was turned off. Every state MUST link to the notification preferences.
- **FR-013**: Every notification email, digest email and page this feature adds MUST be replaceable
  by overriding one template.
- **FR-014**: The documentation MUST cover installing the two extras together, the settings
  needed, sending the digests daily and weekly, and overriding the email templates.
- **FR-015**: Every string the feature shows MUST be translatable.

### Traceability

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-003, FR-004, FR-006, FR-007, FR-008, FR-013, FR-014, FR-015, FR-017 |
| US2 | FR-005, FR-006, FR-007, FR-015, FR-016 |
| US3 | FR-009, FR-010, FR-011, FR-012, FR-013, FR-015 |

### Key Entities

- **Channel**: a way a notification reaches a person. This feature adds email beside the site.
  Owned by django-generic-notifications.
- **Notification preferences**: a person's choice, per notification type, of which channels it
  reaches them on and how often its email comes. Owned by django-generic-notifications.
- **Digest**: several notifications gathered into one email, daily or weekly. Owned by
  django-generic-notifications.
- **Unsubscribe link**: a link in a notification or digest email that turns that email off for the
  person it was sent to, without them signing in.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer whose project uses the notifications extra sends its notifications by
  email by installing the mail extra and applying the documented settings, with no change to the
  code that sends notifications.
- **SC-002**: A person who chooses a digest for every notification type receives at most one
  notification email a day, or a week.
- **SC-003**: A person stops a notification email from their mail app in one action, or from the
  email's link in two, without signing in.
- **SC-004**: No unsubscribe changes a preference the email it came from did not cover.

## Assumptions

- django-generic-notifications provides email as a channel, the daily and weekly frequencies, the
  per-type preferences and the sending of due digests. django-post-office queues and logs the
  email. This package adds no models of its own.
- The host project declares its notification types, which channels each is always sent on, and each
  type's default frequency.
- The demo project installs both extras and sends sample notifications, so notification and digest
  emails can be seen in its delivery log.
- Push, reminders and choosing the time of day a digest is sent are not part of this feature (R5,
  R6).
