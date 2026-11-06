# django-mvp-community

The vocabulary of django-mvp-community: the words to use in issues, commit
messages, test names, docstrings and documentation. This package sits between
several libraries that use the same English words for different things, so the
meanings below are the ones that hold here.

## Core concepts

**Host project**:
The Django project that installs this package. It owns the theme, the base
template, the data and the URLs. This package renders into it and decides none
of those.
_Avoid_: consumer, client, downstream, user (a user is a person using the host
project, not the project itself).

**Component**:
A Cotton template this package ships, placed on a page with a tag. The tag name
is the file path, so renaming the file changes the public API.
_Avoid_: widget, partial, include, block.

**Extra**:
A feature a host project installs on request, named at install time:
`notifications`, `mail`, `activity` or `sharecards`. An extra brings the
packages its feature is built on. Nothing in the base install depends on one.
_Avoid_: plugin, module, add-on.

**Integration module**:
A Python module in this package that imports an extra's packages. A host
project imports it only when it uses that extra, so the base install never
imports a package it may not have. Each extra has one, named
`mvp_community.integrations.<extra>`, as a module or a package. Nothing outside
`mvp_community.integrations` imports an extra's packages.
_Avoid_: adapter, backend.

**Notification**:
One message to one person about something that happened, either read or unread.
_Avoid_: alert (django-mvp uses that for a message on a page), message
(Django's messages framework).

**Notification type**:
A kind of notification a host project declares, such as "reply received". A
person can turn each type on or off.
_Avoid_: category, event.

**Channel**:
A way a notification reaches a person: the site, email or push.
_Avoid_: medium, transport, backend.

**Digest**:
Several notifications gathered into one email, sent daily or weekly instead of
one email each.
_Avoid_: summary, newsletter.

**Notification preferences**:
A person's choice of notification types, channels and digest frequency, set in
the Account Center.
_Avoid_: settings (that word belongs to Django settings).

**Push subscription**:
One browser or installed web app that a person allowed to receive push. One
person can have several.
_Avoid_: device (a subscription belongs to a browser, not a phone), token.

**Reminder**:
A notification sent on a schedule the person sets, in their own timezone.
_Avoid_: alarm, nudge.

**Activity**:
A record that someone did something to something, such as "Anna finished A1
Tenses".
_Avoid_: event, action (the name django-activity-stream gives its model; use it
only when talking about that model).

**Follow**:
A person's choice to see activity about another person or an object.
_Avoid_: subscribe (that word belongs to push subscriptions and to payments).

**Feed**:
A page of activity split into pages, mounted by the host project: what the signed-in person
follows, the whole site, or one object. The package ships the view, not the page.
_Avoid_: stream, timeline.

**Recent activity**:
The newest few activities placed on any page, such as a dashboard, with a link
to the full list when there is more. A feed is the paged list on a page of its
own.
_Avoid_: stream, widget, ticker.

**Share card**:
The preview image shown when a link to a page is shared.
_Avoid_: thumbnail, OG image, social image.

## Terms deliberately not used

**Engine**: implies this package decides who is notified, when, or how. It
does not. The packages it builds on do, and this package presents their
results.

**Real-time**, **live**: imply websockets or server-sent events. Counts here
refresh by polling.
