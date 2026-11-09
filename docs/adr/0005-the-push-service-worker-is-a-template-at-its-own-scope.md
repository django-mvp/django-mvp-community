# ADR 0005 — The push service worker is a template served at its own scope

**Status:** accepted

## Decision

The service worker that shows a push and opens it on a click is the template `mvp_community/push/worker.js`, served by `WorkerView` at `notifications/push/worker.js` among the push extra's URLs, as JavaScript, revalidated on every visit. The push card registers it at its default scope, the path it is served from. It handles only push events and notification clicks, and controls no pages.

The browser's public key is not a setting. It is derived from `WP_PRIVATE_KEY` in django-push-notifications' settings with py-vapid each time the card is drawn.

## Why

A service worker must be served from the site's own origin, so it cannot come from a static file host, and a template lets a project replace it by name like every other template the package ships. Push events and notification clicks reach a registration whatever its scope, so registering below the root costs nothing and never replaces a worker a project already runs at `/` for its installed web app.

Deriving the public key leaves a project with only the two settings django-push-notifications documents, and the two halves of the key can never disagree.

## Revisit if

A browser stops delivering push to a worker registered below the root, in particular on iPhone and iPad Home Screen web apps, or the package needs a worker that controls pages, such as for offline support.
