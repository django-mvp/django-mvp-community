# Sketch: Notifications by web push

## What exists

- **Push subscriptions.** django-push-notifications' `WebPushDevice` stores one per browser:
  `user`, `name`, `active`, `date_created`, `registration_id` (the push endpoint), `p256dh`,
  `auth` and `browser`, where `browser` is one of Chrome, Firefox, Opera, Edge and Safari. `name`
  is free text. Sending to a subscription the push service reports as gone sets `active` to
  false. Its own endpoint for storing a subscription needs Django REST framework, which this
  package does not depend on.
- **Channels.** django-generic-notifications draws a channel for every class registered with its
  registry. The preferences view passes `registry.get_all_channels()` to the page, which draws a
  column of toggles per channel, so a registered push channel gets its column with no change to
  the view. Email registers only with the mail extra (ADR 0003).
- **The preferences page.** `mvp_community/notifications/preferences.html`: the page title, then
  one card holding the grid of types and channels, then Save. Account Center pages use
  `c-mvp.card`, `c-list` / `c-list.row` for a person's records (as on the Following page),
  `c-alert` for a message, and `c-button`. Alpine is on every page.
- **No planning notes.**

## What the screens need from the code

- The preferences page needs to know whether push is set up, and draws the push card and the push
  column only when it is.
- The push card needs the signed-in person's active push subscriptions, newest first, each with a
  readable name of the browser and system ("Chrome on Android"), the kind of device for its icon,
  and when push was turned on.
- The push card needs to know which subscription, if any, is the browser in use. Only the browser
  knows its own push endpoint, so the page compares it after load.
- The state of the browser in use is known only in the browser: whether it can receive push at all,
  whether notifications for the site are blocked, whether it is an iPhone or iPad browser that has
  not been added to the Home Screen, and whether push is on in it. The card is drawn for each.
- Turning push on needs a service worker registered, the browser's permission asked for on the
  button's click and not before, the subscription posted to a view that stores it for the signed-in
  person (one per endpoint), and a test push sent to it at once.
- Stopping a browser needs a POST that removes only the signed-in person's own subscription, then
  a message naming the browser stopped. Stopping the browser in use also unsubscribes it in the
  browser.
- The browser's name needs reading from the request when push is turned on.

## What the sketch faked

- The push channel (`demo/sketch_push.py`, `SketchPushChannel`): registered so the column shows,
  sends nothing.
- The push subscriptions: kept in the session, seeded with `?sketch_devices=none`, `few` or `many`.
- The state of the browser in use: read from `?sketch_browser=offer`, `on`, `denied`,
  `unsupported` or `homescreen`, because a page served over plain HTTP has no push to detect.
- Turning push on: the button waits a moment as if the browser were asking, then posts to a demo
  view that adds "Firefox on Windows" as this browser. No permission is asked and no test push is
  sent.
- Stopping a browser: a demo view that removes it from the session.
- The context processor `demo.sketch_push.push`, and the demo URLs under `sketch/push/`.

## What was ruled by eye

- The push card sits above the grid of types and channels, on the same page. The push column is
  meaningless until a browser receives push, so turning it on comes first.
- Before push is on, the card explains push in one paragraph with the button under it. Once on,
  the explanation gives way to one line saying push is on here.
- Right after push is turned on, a success message inside the card says a test notification is on
  its way.
- A refusal or a block, a browser that cannot receive push, and an iPhone or iPad browser not on
  the Home Screen each replace the button with a message inside the card saying what the person
  can do. None of them offers the button.
- The browsers receiving push are a list inside the same card, each row an icon for the kind of
  device, the browser's name, a second line with when push was turned on, and Stop. The browser
  in use says "This browser" at the start of that second line, with no badge.
- Stop acts at once, with no confirmation: push can be turned on again on any browser the person
  still holds.

- At phone width the grid of types and channels scrolls sideways inside its own box, so the last
  channel column may start out of view. The table keeps its normal size (ruled at the sketch
  review, 2026-11-08).

## Sketch review

Approved by the maintainer on 2026-11-08 with no changes asked for.
