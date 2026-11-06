# ADR 0003 — The notifications extra registers its own email channel

**Status:** accepted

## Decision

When the mail extra is installed beside the notifications extra, the notifications extra unregisters django-generic-notifications' `EmailChannel` and registers `mvp_community.integrations.notifications.channels.NotificationEmailChannel`, a subclass, under the same `email` key. Without the mail extra no email channel is registered, and the site is the only channel. The subclass changes three things and nothing else: it sends through Django's mail backend with the one-click unsubscribe headers, it writes each email in the language `recipient_language` returns, and it emails a type the project always sends by email at once. The library's rendering, template names and digest sending are called, never copied.

A notification type that names an email channel in `required_channels` or `default_channels` names `NotificationEmailChannel`. System check `mvp_community.E001` reports a type that names the library's class while this package's is registered.

The extra also registers a weekly digest frequency and unregisters the library's own "System Message" type, so a project's preferences list only the types it declares.

## Why

The unsubscribe headers have to be set where the email is built, and the library offers no hook for headers: its `send_email` is the documented override point, and only a subclass reaches it. A wrapping email backend would have to guess which emails are notifications.

django-generic-notifications compares channel classes by identity when it checks a type's required and default channels (`generic_notifications/types.py`, `get_enabled_channels`). A subclass registered under `email` therefore does not match a type that names the library's class, and that email would silently stop. The system check turns that silence into an error at start-up, naming the class to use.

Registering no email channel without the mail extra keeps the preferences page from offering email that would leave through whatever `EMAIL_BACKEND` happens to be set, unqueued and unlogged.

## Revisit if

django-generic-notifications compares channels by key, or offers a hook for an email's headers, either of which would let the library's own channel stay registered.
