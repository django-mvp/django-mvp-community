# ADR 0004 — Web push is an extra of its own

**Status:** accepted

## Decision

Web push is the `push` extra, separate from `notifications`. It installs django-push-notifications with its web push dependencies, ua-parser, py-vapid and cryptography, and its code lives in `mvp_community.integrations.push`. When `push_notifications` is in `INSTALLED_APPS` beside `generic_notifications`, the package registers `PushChannel` under the key `push` with django-generic-notifications. Without it no push channel is registered, and the notification preferences page draws no push card and no push column.

The notifications integration reaches the push module only from inside the branch where a `push` channel is registered, so the notifications extra never imports a push package.

## Why

pywebpush, which django-push-notifications needs to send web push, brings aiohttp, cryptography, requests, http-ece and py-vapid. Inside the `notifications` extra every project with notifications would carry them, pushing or not, which the goal that a project never carries the packages of a feature it does not use rules out. An extra of its own costs one more name at install time, and keeps push installable on its own terms, as mail is.

Keying the card and the column on the registered channel, rather than on installed apps, mirrors how the page already decides whether to offer email frequencies, and means a project that unregisters the channel hides push everywhere at once.

## Revisit if

django-push-notifications sends web push without pywebpush's dependency tree, or push becomes something every project using notifications installs anyway.
