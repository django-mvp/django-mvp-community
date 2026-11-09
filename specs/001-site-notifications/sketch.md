# Sketch: Notifications on the site

## What exists

- **Data.** django-generic-notifications supplies everything the screens read. A notification has a recipient, a type, a subject, a text, a link, an actor, a target object, when it was added and when it was read. A notification type is declared in Python with a name, a description and channels that are required, forbidden or on by default. Preferences are stored per person, type and channel, and only where they differ from the default.
- **What the package already does.** It counts unread notifications on a channel, lists them for a person, marks some or all read, reads a person's preferences as a type-by-channel grid, and saves that grid from a form's fields.
- **What the package registers by itself.** Two channels, the site and email, and one type, "System Message", which must go by email. Both appear on the preferences page as soon as the package is installed.
- **The shell.** The header draws the widgets named in `MVP_CONFIG["layout"]["navbar"]["end"]`, so the bell is one of them. htmx is bundled, so the count refreshes with a poll. The Account Center takes an entry in `AccountCenterMenu` and a card in `account.cards`, the same way django-mvp-accounts adds its pages.
- **Components.** daisy-cotton's `list` and `list.row` for the notifications, `indicator` for the count on the bell, `form.toggle` for each choice, and django-mvp's `card`, `pagination`, `page.title` and Account Center page.
- **Planning notes.** The one note names django-generic-notifications. The sketch is built on it.

## What the screens need from the code

- The bell needs the signed-in person's unread count on the site on every page, and a way to fetch it again without the page.
- The notifications page needs one page of the person's notifications, newest first, with whether each is read.
- Opening a notification needs an address that marks it read and goes on to its link.
- Mark all read needs a form post that marks every one of the person's notifications read.
- The preferences page needs every declared type against every registered channel, with the person's choice and whether that choice is required or forbidden, and a post that saves it.
- The Account Center card and entry need to appear only when the notifications URLs are included.
- Each page's own title needs to reach the browser's title bar. The sketch's preferences page shows only "Account Center" there.

## What the sketch faked

- The notification types are the demo's own four, in `demo/notifications.py`.
- The notifications come from `seed_notifications`, written straight into the database rather than sent.
- Every seeded notification links to the home page.
- The bell is switched on by naming it in the demo's settings, and the icons `notifications` and `notifications.preferences` are registered in the demo's settings. A host project would have to do both.
- The Account Center menu entry is registered from the demo's app config.
- The context processor that gives the bell its first count, and `django.contrib.humanize` for the "2 hours ago" times, are added in the demo's settings.
- "Send me a notification" on the overview page exists only so the bell's count can be watched rising.
- The email column on the preferences page and the "System Message" row are the package's defaults, shown as they come.

## What was ruled by eye

- Every page is built from django-mvp and daisy-cotton components and the classes django-mvp's stylesheet already ships, with no styles of its own.
- The pages belonging to the Account Center sit under its address, `account/`, so the preferences page is at `account/notifications/`. The notifications page and the bell stay under `notifications/`.
- The "System Message" row and the Email column, which django-generic-notifications registers by itself, stay on the preferences page for now.
