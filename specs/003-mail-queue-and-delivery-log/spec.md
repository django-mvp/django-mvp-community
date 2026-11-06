# Feature Specification: Queue, log and send a project's email through the mail extra

**Feature Branch**: `003-mail-queue-and-delivery-log`

**Created**: 2026-11-06

**Status**: Draft

**Serves**: G4, email from the project matches its look, is translated, and can be gathered into a
digest and unsubscribed from. This feature delivers the queued, logged and translated part. The
look is django-mvp's email layout. Digests and unsubscribing come with notification email (R4).

**Roadmap**: R2, email that looks like the application

**Issue**: #18

**Input**: A host project's email comes from many places: django-mvp-accounts,
django-mvp-payments, django-mvp-compliance, allauth and the project's own code. Installing this
package with the mail extra brings django-post-office and django-anymail. With the documented
settings, every email the project sends goes through them without any change to the code that
sends it. It is queued instead of sent during the request, logged with whether it was delivered,
and handed to whichever provider django-anymail is configured for. Staff can keep an email's
wording, and a translation of it for each language, in the database and change them without a
deploy. Those emails use django-mvp's email layout like every other email the project sends. The
documentation covers installing the extra, the settings it needs and writing an email. The project
still chooses the provider. Digests and unsubscribing come later, with notification email.

## Clarifications

### Session 2026-11-06

- Q: Which emails can staff edit in the database? → A: Only email the host project sends from a
  stored template. Email from allauth and the django-mvp packages keeps its own file templates. It
  is queued and logged like every other email, and its wording stays where those packages put it.
- Q: Does the package run something to send queued email? → A: No. The documentation explains how
  a host project sends what is queued, on a schedule or as a background task, and how to send
  each email at once instead. Email sent at once is still logged.
- Q: Where do staff see what was sent? → A: In the admin pages of the package the log belongs to.
  This feature adds no page of its own for it.
- Q: What does "delivered" mean in the log? → A: Whether the provider accepted the email, when,
  and why it failed if it did. What happened after the provider accepted it (delivered, bounced,
  rejected) is not recorded. A project that needs per-recipient bounce figures uses a dedicated
  email marketing service (Sam, 2026-11-06).
- Q: In which language is a stored email sent? → A: The one the sending code names, normally the
  recipient's. A language with no translation of that email falls back to the email's own wording.
- Q: Which layout does a stored email use? → A: django-mvp's email layout, the same as every other
  email the project sends, so a stored email and a file template look alike.
- Q: Does this change how django-mvp, django-mvp-accounts or any other package sends email? → A:
  No. None of them needs this package or the mail extra. The extra changes where their email goes,
  through the project's settings alone.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer sends the project's email through the mail extra (Priority: P1)

A developer building a site on django-mvp installs this package with the mail extra and follows the
documented settings, naming the provider their email should leave through. From then on every email
the project sends, from allauth, the django-mvp packages and their own code, is queued instead of
sent while a page loads, sent to the provider from the queue, and logged. Where the developer's own
code sends an email, they can send it from a stored template by name, in the recipient's language,
and it arrives in django-mvp's email layout.

**Why this priority**: Nothing else in the feature, or in the notification email that follows it,
works until a project's email goes through the queue and the log.

**Independent Test**: Install the extra in a project, apply the documented settings, sign up through
allauth and send an email from the project's own code, then find both emails queued, send the
queue, and find both logged as sent.

**Acceptance Scenarios**:

1. **Given** a project with the mail extra installed and the documented settings applied, **When**
   any code in the project sends an email, **Then** the email is queued and logged, and is not sent
   while the request is handled.
2. **Given** queued email, **When** the project sends its queue, **Then** each email is handed to
   the configured provider and the log records whether the provider accepted it.
3. **Given** a project set to send each email at once, **When** any code sends an email, **Then**
   it is sent during the request and still logged.
4. **Given** a stored template with a translation for the recipient's language, **When** the
   developer's code sends that template by name in that language, **Then** the email is written in
   that translation and laid out in django-mvp's email layout.
5. **Given** a stored template with no translation for the language asked for, **When** it is sent
   in that language, **Then** the email is written in the template's own wording.
6. **Given** a provider that refuses an email or cannot be reached, **When** the queue is sent,
   **Then** the log records the failure and its reason, and the email is tried again as the
   project's settings allow.
7. **Given** a project that has not installed the mail extra, **When** it sends email, **Then** it
   is sent exactly as before, and nothing that belongs to the extra is imported.

---

### User Story 2 - Staff check what was sent and whether it arrived (Priority: P1)

A member of staff wants to know whether someone got an email. They open the email log in the admin,
find the emails sent to that person, and see for each one when it was sent and whether the
provider accepted it. A failed email shows why it failed.

**Why this priority**: The log is half of the reason for the feature. Without it, "did they get the
email" has no answer short of asking the provider.

**Independent Test**: Send several emails to two people, one of which fails, then find the emails to
one person in the admin and read their status and the failure's reason.

**Acceptance Scenarios**:

1. **Given** logged emails, **When** a member of staff opens the email log, **Then** it lists the
   emails newest first with each one's recipients, subject, time and status.
2. **Given** emails to several people, **When** staff search for one recipient's address, **Then**
   only the emails to that address are listed.
3. **Given** an email that failed, **When** staff open it, **Then** they see the reason it failed.
4. **Given** a person who is not staff, **When** they try to open the email log, **Then** they are
   refused.

---

### User Story 3 - Staff change an email's wording and its translations without a deploy (Priority: P2)

A member of staff wants an email the project sends from a stored template to read differently, in
one language or in several. They open the stored template in the admin, change its subject and
wording, add or change its translation for each language, and save. The next email sent from it
carries the new wording, with no code change or deploy.

**Why this priority**: Queueing and the log are useful without it, and only email the project sends
from a stored template can be changed this way.

**Independent Test**: Store a template with an English wording and a German translation, change
the German subject in the admin, send the template in German, and receive the new subject.

**Acceptance Scenarios**:

1. **Given** a stored template, **When** staff change its subject or wording and save, **Then** the
   next email sent from it carries the change.
2. **Given** a stored template, **When** staff add a translation for a language, **Then** the next
   email sent from it in that language carries the translation, and other languages are unchanged.
3. **Given** a change to a stored template that would not render, **When** staff save it, **Then**
   it is refused with the reason, and email sent from it carries on as before.
4. **Given** a person who is not staff, **When** they try to open the stored templates, **Then**
   they are refused.

---

### Edge Cases

- The queue is not sent for a while: emails wait in the queue and are sent in order of priority
  once it is, and none is lost.
- A stored template is sent with a variable the sending code did not supply: the email is still
  sent, with that part empty, as for any Django template.
- A stored template is deleted while emails sent from it are in the log: the log keeps those
  emails as they were sent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Installing the mail extra MUST bring django-post-office and django-anymail, and
  installing the package without it MUST import nothing that belongs to it.
- **FR-002**: With the documented settings, every email the host project sends MUST be queued and
  logged, with no change to the code that sends it, whichever package sends it.
- **FR-003**: Queued email MUST leave through the provider the host project configures for
  django-anymail. This package MUST NOT choose a provider.
- **FR-004**: The package MUST NOT run anything that sends the queue. A host project MUST be able
  to send its queue on a schedule, as a background task, or send each email at once, and email sent
  at once MUST still be logged.
- **FR-005**: The log MUST record, for every email, its recipients, subject, time, whether the
  provider accepted it and, when it failed, why.
- **FR-006**: The feature MUST NOT record what happens to an email after the provider accepts it.
- **FR-007**: A host project MUST be able to send an email from a stored template by name, in a
  language it names, and the email MUST be written in that language's translation, or the
  template's own wording where it has none.
- **FR-008**: An email sent from a stored template MUST be laid out in django-mvp's email layout.
- **FR-009**: Staff MUST be able to change a stored template's subject and wording, and its
  translation for each language, in the admin, and the change MUST apply to the next email sent from
  it.
- **FR-010**: Staff MUST be able to list logged emails newest first, find the emails to one address,
  and see each email's status and any failure reason.
- **FR-011**: The email log and the stored templates MUST be open to staff only.
- **FR-012**: The documentation MUST cover installing the extra, the settings it needs, sending the
  queue, and writing and sending a stored template.
- **FR-013**: Every string the feature shows MUST be translatable.

### Traceability

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-012, FR-013 |
| US2 | FR-005, FR-010, FR-011, FR-013 |
| US3 | FR-007, FR-009, FR-011, FR-013 |

### Key Entities

- **Queued email**: an email waiting to be sent, not yet handed to the provider. Owned by
  django-post-office.
- **Delivery log**: the record of each email the project sent, whether the provider accepted it,
  and why it failed if it did. Owned by django-post-office.
- **Stored template**: an email's subject and wording kept in the database, with a translation per
  language, which staff change in the admin. Owned by django-post-office.
- **Provider**: the service an email leaves through, configured for django-anymail by the host
  project.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer routes all of an existing django-mvp project's email through the queue
  and the log by installing the extra and applying the documented settings, changing no code that
  sends email.
- **SC-002**: Staff see from the admin alone whether the provider accepted an email to a person,
  and why it failed if it did.
- **SC-003**: Staff change a stored email's wording in any language and the next email carries it,
  with no code change or deploy.
- **SC-004**: No email is sent during a request once the project uses the queue.

## Assumptions

- django-post-office provides the queue, the log, stored templates with their translations, and
  their admin pages. django-anymail provides the providers. This package
  adds no models of its own.
- The host project decides which language an email is sent in when it sends it.
- The admin pages are django-post-office's own. Their look is whatever the host project's admin
  has.
- The demo project installs the mail extra and sends its sample emails through it, so the queue and
  the log can be seen there.
- Digests, notification email and unsubscribing are not part of this feature (R4).
