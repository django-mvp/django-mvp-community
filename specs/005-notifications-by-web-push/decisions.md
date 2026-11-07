# Decisions: Notifications by web push

Every decision below was made while the specification was written, where the issue was silent.

## D1 — Push ships in the notifications extra and is off until it is set up

**Decision:** django-push-notifications, with the web push dependencies it names, is added to the
`notifications` extra. Push is a channel only once the project adds django-push-notifications'
app and the push settings. Without them the preferences page shows no push column and offers no
way to turn push on (FR-002), as the page shows no email column without the mail extra.
**Why:** CONTEXT.md and docs/developer/brainstorm.md name four extras and put web push in
`notifications`. A fifth extra would be new public vocabulary for a channel of the same feature.
**Risk:** G2 says a project never carries the packages of a feature it does not use. A project
with notifications but no push carries the web push libraries. Planning weighs their size, and if
it finds that weight unreasonable it proposes a separate extra as an amendment to this decision.
**ADR:** at planning, beside ADR 0003, if the channel registration differs from the email channel's.

## D2 — The package ships the service worker; the host project configures keys and URLs only

**Decision:** the service worker that receives a push and opens its address is a template the
package ships and serves from a URL among the notifications extra's URLs, so a project overrides
it like any other template (G3). It is registered at its own scope, so it never replaces a service
worker the host project already has. The host project creates the key pair, puts it in the
settings django-push-notifications reads, and includes the URLs. The package never creates or
stores keys.
**Why:** a service worker has to be served from the site's own origin, so it cannot come from a
CDN, and a template keeps it overridable. Keys are secrets and belong in the project's settings,
as Article V of the constitution requires.
**Planning checks:** that a worker registered at its own scope receives push inside a web app
installed on a phone's home screen, and how a project with its own service worker for an installed
web app is documented.

## D3 — Push turns on and is listed on the preferences page, not a page of its own

**Decision:** the explanation, the control that turns push on, and the list of a person's push
subscriptions all sit on the notification preferences page (FR-009 to FR-012).
**Why:** the issue puts push on that page as a channel, and a person deciding which types reach
them by push needs to see in the same place whether any browser receives it.

## D4 — The browser asks for permission only when the person asks

**Decision:** opening the preferences page never makes the browser ask. The request follows the
person's own action, on a page that has already explained push (FR-009, SC-003).
**Why:** the issue asks for the explanation before the request, and browsers quieten or block
permission requests made without a user action.

## D5 — Push is sent as it happens and is never gathered into a digest

**Decision:** push is a real-time channel (FR-005). The choice of how often stays an email choice.
**Why:** a digest exists to keep an inbox quiet. A push gathering a day's notifications would
arrive long after any of them mattered.

## D6 — A test push confirms a browser that was just turned on

**Decision:** turning push on sends that browser one push saying push works (FR-010).
**Why:** a phone that is missing a step, such as the home screen, accepts the permission and then
receives nothing. The test push shows at once whether push reaches this browser, rather than at the
next notification.

## D7 — Tapping a push behaves like the bell's list

**Decision:** a push opens the notification's address and marks it read, or opens the
notifications page when it has no address (FR-008).
**Why:** a notification read from a push should not stay unread on the site, and the bell's list
already marks a notification read on the way to its address.

## D8 — A push is written in the recipient's language, as email is

**Decision:** the push text is written in the language the email channel's `recipient_language`
returns for the person (FR-006).
**Why:** Django stores no language per person, and FS-004 (D10) already gave projects one place
to say which language a person reads.

## D9 — Signing out does not stop push

**Decision:** a subscription stays until the person stops it from the list, blocks push in the
browser, or deletes their account (FR-013 to FR-015).
**Why:** a subscription belongs to a browser, not to a session. A person who signs out of a phone
they carry still wants their notifications. The list on every device is the way to stop a browser
someone else now holds.

## D10 — Gone subscriptions drop off on their own

**Decision:** a subscription the push service reports as gone is no longer listed or sent to
(FR-014).
**Why:** django-push-notifications marks such a subscription inactive when a push to it is refused
as gone (`push_notifications/webpush.py`, the 404 and 410 responses). The list shows active
subscriptions only.

## D11 — A push service failure never fails sending

**Decision:** a push that fails is dropped for that subscription, and the notification is still
stored and delivered on the other channels (FR-007).
**Why:** the host project sends notifications inside its own requests and tasks, and a third-party
push service being down must not make them fail.

## D12 — The pages are sketched before planning

**Decision:** this feature's screens are sketched and agreed with the maintainer before anything is
planned.
**Why:** turning push on is a flow across several steps, with a different message for a refusal, a
blocked browser, a browser that cannot receive push and a phone that needs the home screen first,
and the list of subscriptions is a part of the page nobody has drawn.
