# Feature Specification: Notifications by web push

**Feature Branch**: `005-notifications-by-web-push`

**Created**: 2026-11-07

**Status**: Draft

**Serves**: G5, notifications reach people by web push as well as on the site and by email,
through the same preferences. This feature delivers it. G1, each person's notification preferences
in the Account Center: push is chosen on the same page as the site and email.

**Roadmap**: R5, web push

**Issue**: #28

**Sketch**: yes, drawn and agreed before the feature is planned. Turning push on is a flow across several steps (an explanation, the browser's
own permission request, and what follows a refusal or a phone that will not accept push yet), and
the list of a person's push subscriptions is a part of the preferences page nobody has drawn.

**Input**: People who use a site built on django-mvp should be able to get their notifications as
push, in their browser or on their phone from the site installed as a web app, as well as on the
site and by email. Push becomes one more channel on the notification preferences page in the
Account Center, so a person turns each notification type on or off for push the same way they
already do for the site and for email. A person turns push on for the browser or device they are
using, sees which of their devices receive push, and can stop any of them. Before the browser asks
for permission, the page explains what push is and what a phone needs before it will accept push
from a web app, since some phones only deliver it to a site added to the home screen. Deciding when
a notification is sent stays with the host project. Reminders are not part of this.

## Clarifications

### Session 2026-11-07

- Q: Where does a person turn push on and see their push subscriptions? → A: On the notification
  preferences page in the Account Center, where push is also a channel for each notification type.
  There is no second page.
- Q: When does the browser ask for permission? → A: Only after the person asks to turn push on, on
  a page that has already explained what push is. Opening the preferences page never makes the
  browser ask.
- Q: Does a push come as it happens, or can it be gathered like a digest? → A: As it happens. The
  choice of how often applies to email alone.
- Q: What does tapping a push do? → A: It opens the notification's address and marks it read, as
  the bell's list does. A notification with no address opens the notifications page.
- Q: How does a person know push works on the browser they just turned on? → A: That browser
  receives one push saying so, straight away.
- Q: What does a person see for each push subscription? → A: The kind of browser and when push was
  turned on, with the one they are using now marked as this browser.
- Q: What happens to a subscription the browser itself has given up, such as after the site's data
  is cleared or the app is removed from the phone? → A: The next push to it is refused by the push
  service, and it drops off the person's list without anyone doing anything.
- Q: Does signing out stop push to that browser? → A: No. Push stops when the person stops it from
  the list, on any of their devices, or blocks it in the browser.
- Q: In which language is a push written? → A: The recipient's, chosen the same way as for email.
- Q: What happens when a project installs the notifications extra but does not set up push? → A:
  Nothing changes. Push is not a channel on the preferences page, the page offers no way to turn
  it on, and nothing is sent.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer sends notifications by push (Priority: P1)

A developer whose project already uses the notifications extra follows the documented settings to
set up push: they create the key pair a push service needs to accept messages from the site, put
it in the project's settings, and include the URLs the documentation lists. Push then appears as a
channel on every person's notification preferences page, beside the site and, when the mail extra
is installed, email, and each notification a person has left on for push reaches every browser
where they turned push on. The code that sends notifications does not change. The developer can
change how the push controls look by overriding one template.

**Why this priority**: No person can receive a push until a project can send one.

**Independent Test**: In a project with push set up, send a notification to a person who has push
on for its type and one push subscription, and find a push delivered to that subscription. Leave
push unconfigured and find the preferences page and sending unchanged.

**Acceptance Scenarios**:

1. **Given** a project with push set up as documented, **When** a person opens their notification
   preferences, **Then** push is listed as a channel for each notification type, beside the
   channels the project already has.
2. **Given** a person with push on for a notification type and push turned on in two browsers,
   **When** the project sends them a notification of that type, **Then** a push about it is sent
   to both browsers, in the person's language.
3. **Given** a person with push off for a notification type, **When** the project sends them a
   notification of that type, **Then** no push is sent and the notification still reaches them on
   the other channels they have on.
4. **Given** a person who has push on for a type but has not turned push on in any browser,
   **When** the project sends them a notification of that type, **Then** nothing is sent by push
   and nothing fails.
5. **Given** a notification type the host project always sends by push, **When** a person opens
   their preferences, **Then** push is shown as always on for that type and cannot be turned off.
6. **Given** a project with the notifications extra installed and push not set up, **When** a
   person opens their notification preferences and receives notifications, **Then** push is not
   listed, nothing offers to turn it on, and no push is sent.
7. **Given** a project that has the push packages but is missing a setting push needs, **When** the
   project starts, **Then** Django's system checks report which setting is missing.
8. **Given** a push service that is slow or refuses a push, **When** the project sends a
   notification, **Then** the notification is still stored and delivered on the other channels,
   and sending does not fail.
9. **Given** a project that overrides the template of the push controls, **When** a person opens
   their preferences, **Then** the project's template is used.
10. **Given** a project that names an icon for its pushes, and a notification type that names one
    of its own, **When** the project sends a notification, **Then** its push carries the type's
    icon if it has one, otherwise the project's, otherwise the site's own icon, and no icon when
    there is none of these.

---

### User Story 2 - A person turns push on for the browser they are using (Priority: P1)

A person who wants to hear about notifications when the site is closed opens their notification
preferences in the Account Center on their laptop or phone. The page explains what push is and,
on a phone, what the phone needs first, such as adding the site to the home screen. They ask to
turn push on, the browser asks their permission, and they allow it. That browser receives a push
saying push now works, and from then on each notification they have on for push arrives there as a
push, which opens the notification when they tap it.

**Why this priority**: It is the feature as a person meets it: without it nobody has a push
subscription for the project to send to.

**Independent Test**: On a browser that supports push, open the preferences page, turn push on and
allow it, and receive the push saying it works. Have a notification sent that is on for push,
receive it, tap it, and land on the notification's address with it marked read.

**Acceptance Scenarios**:

1. **Given** a person on their notification preferences page in a browser that supports push and
   has not been turned on, **When** the page loads, **Then** it explains what push is and offers to
   turn it on, and the browser has not asked for permission.
2. **Given** that page, **When** the person asks to turn push on and allows it when the browser
   asks, **Then** a push subscription is stored for them, the browser receives a push saying push
   works, and the page shows push as on for this browser.
3. **Given** a person who refuses when the browser asks, **When** the page updates, **Then** no
   subscription is stored and the page says push is blocked in this browser and how to allow it
   from the browser's own settings.
4. **Given** a browser in which push is already blocked for the site, **When** the person opens the
   page, **Then** it does not offer to turn push on and says how to allow it from the browser.
5. **Given** a phone that only accepts push from a site added to its home screen, **When** the
   person opens the page in the phone's browser, **Then** the page says how to add the site to the
   home screen and turn push on from there, and does not offer to turn it on in the browser.
6. **Given** a browser that cannot receive push at all, **When** the person opens the page,
   **Then** it says this browser cannot receive push and does not offer to turn it on.
7. **Given** a person who has push on in this browser, **When** a notification they have on for
   push is sent, **Then** it arrives as a push, and tapping it opens the notification's address and
   marks the notification read. A notification with no address opens the notifications page.
8. **Given** a person who turns push on again in a browser that already has it, **When** it
   completes, **Then** they still have one subscription for that browser, not two.
9. **Given** a page without script, **When** the person opens their preferences, **Then** the rest
   of the page works and the push controls say script is needed to turn push on.

---

### User Story 3 - A person sees and stops their push subscriptions (Priority: P2)

A person who has turned push on in several places, such as a work laptop, a phone and an old
tablet, opens their notification preferences. They see each browser that receives their push, what
kind it is and when push was turned on there, with the one in their hand marked. They stop push to
the old tablet, or to the browser they are using, and no push reaches it again.

**Why this priority**: A person can already stop push in one browser by blocking it there, so this
is how they stop it everywhere else, including on a device they no longer have.

**Independent Test**: Turn push on in two browsers, stop one of them from the other, have a
notification sent, and find a push on the remaining browser only.

**Acceptance Scenarios**:

1. **Given** a person with push turned on in several browsers, **When** they open their
   preferences, **Then** each is listed with the kind of browser and when push was turned on, and
   the one they are using is marked as this browser.
2. **Given** that list, **When** the person stops push to one browser, **Then** it is removed from
   the list and no push is sent to it again, and the others keep receiving push.
3. **Given** a person who stops push to the browser they are using, **When** the page updates,
   **Then** it shows push as off for this browser and offers to turn it on again.
4. **Given** a subscription the push service reports as gone, **When** the next push to it is
   refused, **Then** it is no longer listed and no further push is sent to it.
5. **Given** a person with no push subscriptions, **When** they open their preferences, **Then** no
   list is shown and the page offers to turn push on in this browser.
6. **Given** a request to stop a push subscription that belongs to another person, **When** it is
   sent, **Then** nothing is changed.
7. **Given** a person who has not signed in, **When** they ask to turn push on or to stop a
   subscription, **Then** nothing is changed.

---

### Edge Cases

- A person deletes their account: their push subscriptions are removed and no push reaches any of
  their browsers again.
- Two people share one browser and both turn push on: each person's subscription is their own, and
  stopping one leaves the other.
- A person turns push on for a browser while push is off for every notification type: the browser
  receives the push saying push works, and nothing more until a type is on for push.
- A notification type is no longer registered by the host project: no push is sent for it.
- The project's push key pair is replaced: existing subscriptions stop receiving push, and each
  person turns push on again. The documentation says so.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: With the notifications extra installed and push set up as documented, push MUST be a
  channel on the notification preferences page, and notifications MUST be sent by push to people
  who have it on for their type.
- **FR-002**: With push not set up, the preferences page MUST NOT list push or offer to turn it on,
  and no notification MUST be sent by push.
- **FR-003**: When the push packages are installed and a setting push needs is missing, Django's
  system checks MUST report the missing setting.
- **FR-004**: A notification MUST be pushed to every push subscription of its recipient, and to
  none of anyone else's, and MUST NOT be pushed to a person who has push off for its type.
- **FR-005**: A push MUST be sent as the notification happens, and MUST NOT be gathered into a
  digest. The choice of how often MUST continue to apply to email alone.
- **FR-006**: A push MUST be written in the recipient's language, chosen as it is for email.
- **FR-007**: A push service that fails or refuses a push MUST NOT stop the notification being
  stored or sent on other channels, and MUST NOT make sending fail.
- **FR-008**: Tapping a push MUST open the notification's address and mark it read, or open the
  notifications page when it has no address.
- **FR-009**: The preferences page MUST explain what push is before the browser asks for permission,
  and the browser MUST ask only after the person asks to turn push on.
- **FR-010**: Turning push on MUST store one push subscription for the signed-in person and that
  browser, MUST NOT store a second for a browser that already has one, and MUST send that browser a
  push saying push works.
- **FR-011**: The preferences page MUST tell the person, and offer no way to turn push on, when push
  is blocked in the browser, when the browser cannot receive push, and when the phone only accepts
  push from a site added to the home screen, saying in each case what the person can do.
- **FR-012**: The preferences page MUST list the signed-in person's push subscriptions, each with
  the kind of browser and when push was turned on, marking the browser in use.
- **FR-013**: A person MUST be able to stop push to any of their own subscriptions, after which no
  push is sent to it. A request about another person's subscription, or from someone not signed in,
  MUST change nothing.
- **FR-014**: A subscription the push service reports as gone MUST stop being listed and MUST NOT be
  sent to again.
- **FR-015**: Deleting a person's account MUST remove their push subscriptions.
- **FR-016**: The rest of the preferences page MUST work without script, and the push controls MUST
  say that turning push on needs script.
- **FR-017**: Every template this feature adds MUST be replaceable by overriding that one template.
- **FR-018**: The documentation MUST cover setting up push, creating the key pair, the URLs to
  include, naming push in a notification type's channels, what replacing the key pair does, and
  what phones need before they accept push from a web app.
- **FR-019**: Every string the feature shows, on the page and in a push, MUST be translatable.
- **FR-020**: Every push MUST carry an icon as an absolute address: the notification type's own
  when it names one, otherwise the one the project names, otherwise the site's own icon. With
  none of these, a push MUST carry no icon.

### Traceability

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-017, FR-018, FR-019, FR-020 |
| US2 | FR-008, FR-009, FR-010, FR-011, FR-016, FR-017, FR-019 |
| US3 | FR-012, FR-013, FR-014, FR-015, FR-017, FR-019 |

### Key Entities

- **Channel**: a way a notification reaches a person. This feature adds push beside the site and
  email. Owned by django-generic-notifications.
- **Push subscription**: one browser or installed web app that a person allowed to receive push.
  One person can have several. Owned by django-push-notifications.
- **Notification preferences**: a person's choice, per notification type, of the channels it reaches
  them on, now including push. Owned by django-generic-notifications.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer whose project uses the notifications extra sends its notifications by push
  by applying the documented settings, with no change to the code that sends notifications.
- **SC-002**: A person turns push on for the browser they are using from the preferences page in
  two actions: asking to turn it on, and allowing it when the browser asks.
- **SC-003**: Opening the preferences page never makes the browser ask for permission.
- **SC-004**: After a person stops push to a browser, no further push reaches it.
- **SC-005**: A project that does not set up push sees no change to its preferences page or its
  sending.

## Assumptions

- django-push-notifications stores push subscriptions and sends web push. django-generic-notifications
  decides who receives which notification on which channel. This package adds no models of its own.
- The host project decides when notifications are sent, which channels each type is always sent on,
  and which are on by default. Push follows a type's declared defaults like any other channel.
- The host project serves its pages over HTTPS in production, which browsers require for push.
- The demo project sets up push and sends sample notifications, so the push controls and a push can
  be tried in it.
- Native phone apps, reminders and quiet hours are not part of this feature (R6, and Article XII of
  the constitution).
