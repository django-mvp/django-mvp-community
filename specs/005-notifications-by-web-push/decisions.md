# Decisions: Notifications by web push

Every decision below was made while the specification was written, where the issue was silent.

## D1 — Push is an extra of its own, and is off until it is set up

**Decision:** django-push-notifications with its web push dependencies, and ua-parser, form a fifth
extra, `push`, with its own integration module, `mvp_community.integrations.push`. Push is a
channel only once the project installs that extra and adds django-push-notifications' app and
settings. Without them the preferences page shows no push card or column (FR-002), as the page
shows no email column without the mail extra.
**Why:** pywebpush brings aiohttp, cryptography, requests, http-ece and py-vapid. Inside the
`notifications` extra, every project with notifications would carry them whether it pushes or
not, which G2 rules out. The brainstorm put push in `notifications` before the dependency tree was
looked at.
**ADR:** to be decided at convergence, with D2.

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

**Decision:** the push channel has its own `recipient_language`, returning `LANGUAGE_CODE` like the
email channel's (FR-006). A project that stores a language per person overrides both.
**Why:** Django stores no language per person. The email channel exists only with the mail extra,
so the push channel cannot borrow its method.

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

## D13 — One existing test fixture removes the push channel too

**Decision:** the `without_mail` fixture in the notifications view tests keeps only the website
channel, so it now removes `push` as well as `email`.
**Why:** the suite runs every extra, so push is registered in it. The fixture's tests describe a
project with the site as its only channel, which is still what they assert.

## D14 — The public key is derived from the private key

**Decision:** the page reads the public key from the private key django-push-notifications already
holds, with py-vapid. There is no setting for it.
**Why:** one setting fewer, and the two can never disagree.

## D15 — The service worker is served by a view from a template, at its own scope

**Decision:** `notifications/push/worker.js` renders `mvp_community/push/worker.js`. It controls no
pages.
**Why:** a worker must come from the site's origin, and a template keeps it overridable (G3).
Push and notification clicks reach a registration whatever its scope.

## D16 — A subscription stores the user agent, and its name is read when the page is drawn

**Decision:** `WebPushDevice.name` holds the request's user agent. The list reads the browser's
family, where it runs and the kind of device from it with ua-parser each time the page is drawn,
and words the label in the reader's language.
**Why:** a label stored once, in the language of the request that turned push on, cannot be
translated for whoever reads the list (FR-019), and the device kind would have to be guessed back
from a sentence.
**ADR:** none — local to this feature's list.

## D17 — Only the push services browsers use are accepted as endpoints

**Decision:** the subscribe view refuses an endpoint whose host is not Google's, Mozilla's,
Apple's or Microsoft's push service.
**Why:** the server posts to every stored endpoint on every notification. Any address would let a
signed-in person make the server send requests where they choose, and stall other people's
requests with addresses that never answer.
**ADR:** none — a validation rule of one view, documented on the push page.

## D18 — Stopping the browser in use leaves the browser's own subscription alone

**Decision:** Stop deletes the person's row and nothing more. No script unsubscribes the browser.
**Why:** two people sharing a browser share its endpoint, so unsubscribing it would stop the other
person's push too. The page then offers to turn push on again in that browser.
**ADR:** none — follows from the spec's shared-browser edge case.

## Rulings at the design review

Three high findings were applied to the plan: the system check reads the library's own settings
dict and tests for an empty value (D14's check); endpoints are restricted to push services (D17);
the browser helpers became one `Browser` class (D16). Medium and low findings were applied as plan
edits as well: request errors are caught per subscription, the public key is not cached, the
`browser` field keeps its default, Stop runs no script (D18), and tests were added for the
registration without the package, the card's override and a digest preference.
