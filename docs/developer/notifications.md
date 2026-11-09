# Notifications

Notifications gives a django-mvp project a bell in the header with the signed-in person's unread count, a page listing their notifications, and an Account Center page where they choose which notification types they receive and on which channel. It is built on [django-generic-notifications](https://github.com/loopwerk/django-generic-notifications), which stores the notifications and decides who receives what. This package supplies the pages around it. It adds no models and no migrations of its own.

Declaring notification types and sending notifications are done with django-generic-notifications, as described in its own documentation. This page covers what you add to a project to show them.

## Install notifications

Install the extra, add four settings and include the URLs.

1. Install the `notifications` extra:

   ```bash
   pip install "django-mvp-community[notifications]"
   ```

2. Add `generic_notifications` and `django.contrib.humanize` to `INSTALLED_APPS`, after `mvp_community`, which sits above `mvp` so its Account Center card is used. The notifications page says when each notification arrived as "2 hours ago", which `humanize` supplies:

   ```python
   INSTALLED_APPS = [
       # ...
       "mvp_community",
       "mvp",
       "generic_notifications",
       "django.contrib.humanize",
   ]
   ```

3. Put the bell in the header by naming its component in `MVP_CONFIG`. Keep whatever else your project already lists in `navbar.end`:

   ```python
   MVP_CONFIG = {
       "layout": {
           "navbar": {
               "end": [
                   "mvp_community.notifications.bell",
                   "mvp.actions.theme-controller",
                   "mvp.actions.login",
               ],
           },
       },
   }
   ```

4. Register the two icons the pages draw, `notifications` and `notifications.preferences`, in your `EASY_ICONS` setting. An icon name that is not registered raises an error rather than drawing nothing:

   ```python
   EASY_ICONS = {
       "default": {
           # ...
           "icons": {
               "notifications": "bi bi-bell",
               "notifications.preferences": "bi bi-sliders",
           },
       },
   }
   ```

5. Include the URLs at the root of your site, beside `mvp.urls`:

   ```python
   urlpatterns = [
       # ...
       path("", include("mvp_community.integrations.notifications.urls")),
       path("", include("mvp.urls")),
   ]
   ```

6. Create django-generic-notifications' tables:

   ```bash
   python manage.py migrate
   ```

Signed in, the bell now appears in the header, and the Account Center has a Notifications entry and a card. The routes are listed under [Pages and routes](#pages-and-routes).

## Send notifications by email

Email is a channel of the preferences page only when the mail extra is installed, because its messages are queued and logged by django-post-office. Without the mail extra the website is the only channel and the preferences page draws no email column.

1. Install the `mail` extra and set it up as described in [Mail](mail.md):

   ```bash
   pip install "django-mvp-community[notifications,mail]"
   ```

2. Add `django.contrib.sites` to `INSTALLED_APPS`, set `SITE_ID = 1`, and set the site's domain to the address people reach your site at, such as `example.org`. Every link in an email is built from it, so a domain left as `example.com` sends people to the wrong site. Change it in the admin, or in a data migration.

3. Name the package's email channel, not django-generic-notifications' own, wherever a notification type lists channels:

   ```python
   from generic_notifications.types import NotificationType, register

   from mvp_community.integrations.notifications.channels import NotificationEmailChannel


   @register
   class SecurityNotice(NotificationType):
       key = "security_notice"
       name = "Security notices"
       description = "Sign-ins from a new device and changes to your account"
       required_channels = [NotificationEmailChannel]
   ```

   django-generic-notifications compares channels by identity, so a type that names its own `EmailChannel` stops matching once the package's channel is registered. Django's system check `mvp_community.E001` reports each such type and names the class to use instead.

A notification now reaches a person by email when email is on for its type, they have an address, and the type's frequency is real-time. A type with a required channel is always sent at once, whatever frequency is stored for it. Each email is written on django-mvp's email layout and queued by django-post-office.

## Send notifications by push

Push is a channel of the preferences page only when the `push` extra is installed. It delivers each notification to the browsers a person turned push on in, as it is created, and adds a push column and a card to the preferences page. Installing it, the signing key it needs and its options are described in [Push](push.md).

## What django-generic-notifications adds by itself, and what this package changes

django-generic-notifications registers an Email channel, a "System Message" notification type and two frequencies, real-time and daily. When the notifications extra starts, `mvp_community.integrations.notifications.setup.configure` changes that:

- It registers a weekly frequency beside the daily one.
- It removes "System Message", so the preferences page lists only the types your project declares. A project that wants one registers its own type.
- It replaces django-generic-notifications' Email channel with `NotificationEmailChannel`, when the mail extra is installed. Without the mail extra it removes the Email channel and registers none.

`NotificationEmailChannel` is registered under the key `email`, so stored preferences and the existing channel name keep working. `configure` can be called again with either value, and leaves the same registry each time.

Email notifications are sent through Django's own email settings, so configure `EMAIL_BACKEND` before sending any. With the mail extra that is the django-post-office backend.

## Declare a notification type

A person chooses notifications by type, so each kind of notification your project sends is a type. Declare each one with django-generic-notifications' `register` decorator, in a module your app imports when it starts, such as from `AppConfig.ready()`:

```python
from generic_notifications.channels import WebsiteChannel
from generic_notifications.types import NotificationType, register


@register
class ReplyReceived(NotificationType):
    key = "reply_received"
    name = "Replies"
    description = "When someone replies to something you wrote"


@register
class SecurityNotice(NotificationType):
    key = "security_notice"
    name = "Security notices"
    description = "Sign-ins from a new device and changes to your account"
    required_channels = [WebsiteChannel]
```

Every registered type is listed on the preferences page against every channel. A channel the type requires is drawn on and cannot be turned off. A channel it forbids is drawn as unavailable. On a line of its own under each type, a person chooses how often its email arrives: as it happens, as a daily digest or as a weekly digest. The choice is saved with the rest of the page, and a type with nothing saved shows the frequency the type declares. The choice is greyed out while email is off for that type and is kept, so turning email back on does not lose it. A type with a required channel offers no choice, because its email always arrives as it happens. Without the mail extra there is no email channel and no choice is drawn.

The type's `name` and `description`, and the channel names, are shown exactly as django-generic-notifications and your project give them. This package does not translate them.

## Send a notification

Send one with django-generic-notifications' `send_notification`:

```python
from generic_notifications import send_notification

send_notification(
    recipient=user,
    notification_type=ReplyReceived,
    subject="Anna replied to your question",
    text="Try the second exercise first.",
    url="/questions/42/",
)
```

The person sees it on the notifications page and in the bell's count when the website channel is on for that type. A notification with a `url` opens that address and is marked read on the way. One without a `url` is drawn as plain text.

## Send digests

A person who chose a daily or weekly frequency for a type gets that type's notifications in one email, not one email each. The digest holds the person's unread notifications of the types they chose for that frequency, grouped by type. Notifications they have already read, or already been emailed, are left out. A person with none gets no email, and a type with no stored choice follows the frequency the type declares, which is daily unless it says otherwise.

Digests are sent by django-generic-notifications' management command. Run it on a schedule, once for each frequency:

```bash
python manage.py send_notification_digests --frequency daily
python manage.py send_notification_digests --frequency weekly
```

For example, in cron, daily at 07:00 and weekly on Monday at 07:00:

```cron
0 7 * * * cd /srv/site && python manage.py send_notification_digests --frequency daily
0 7 * * 1 cd /srv/site && python manage.py send_notification_digests --frequency weekly
```

`--dry-run` shows what would be sent without sending it. The command logs an unknown frequency and exits 0, so read its log when a digest does not arrive. Weekly digests only exist once `configure` has run, which happens when the extra starts.

## Write email in the person's language

Each email is rendered in the language `NotificationEmailChannel.recipient_language(user)` returns. Django stores no language per person, so the default is the site's `LANGUAGE_CODE`. A project that stores one subclasses the channel, registers the subclass under `email` in place of the package's, and returns it:

```python
from mvp_community.integrations.notifications.channels import NotificationEmailChannel


class ProfileLanguageChannel(NotificationEmailChannel):
    def recipient_language(self, user):
        return user.profile.language
```

Register the subclass from `AppConfig.ready()`, after the notifications extra has started, with `registry.register_channel(ProfileLanguageChannel, force=True)`. Name the subclass, not `NotificationEmailChannel`, in a type's channels, because channels are compared by identity.

## Unsubscribe from notification email

`UnsubscribeLink` in `mvp_community.integrations.notifications.unsubscribe` is the signed address that turns notification email off for one person and the types an email carries. It names no stored record and does not expire, so an old email's link keeps working.

```python
from mvp_community.integrations.notifications.unsubscribe import UnsubscribeLink

link = UnsubscribeLink.for_email(user, ["reply_received", "new_follower"])
link.url()  # "https://example.com/notifications/unsubscribe/<token>/"
```

`for_email` leaves out any type the project always sends by email, and returns `None` when none are left. `url()` is absolute through the current `Site`, so it needs `django.contrib.sites` and the `Site`'s domain set. Reading a link drops the types that have become always-sent since it was made, so an old link never turns off a required type.

Every notification email and digest carries the link: as an "Unsubscribe" link in the footer and as the `List-Unsubscribe` header with `List-Unsubscribe-Post: List-Unsubscribe=One-Click`, which lets a mail app offer its own unsubscribe button. A digest's link names every type in the digest. An email whose types are all always sent by email carries neither the header nor the footer link, and the footer shows only the link to the person's notification preferences.

The link does not expire, and its signed payload holds the person's id and the type keys. The id is signed as text, so the link works with any user model, including one whose primary key is a UUID. Anyone who holds an email can read both, though no one can change them without the signature.

The address opens a page that asks the person to confirm before anything changes, so a mail scanner that opens the link changes nothing. The page works for a signed-out visitor, including in a project that uses `LoginRequiredMiddleware`. A mail app's one-click request (`List-Unsubscribe=One-Click`) is answered with status 200 and no page, or 400 for a link that does not read.

The header reaches mail apps intact when email leaves through a django-anymail provider backend, which hands headers to the provider as they are. Django's own SMTP backend cannot send it intact: the address is longer than one header line, and Python's email package folds a long unbroken value into encoded words, which mail apps do not read as an address. Over SMTP the footer link still works, and the mail app's own button does not appear.

## Refresh the bell after sending

The bell refreshes itself every 60 seconds. To refresh it sooner, for example after a request your own page makes with htmx, answer that request with the `HX-Trigger` header set to `notifications:changed`:

```python
response = HttpResponse(status=204)
response["HX-Trigger"] = "notifications:changed"
```

The bell fetches its own markup from the `bell` route and swaps itself in place. A signed-out request to that route gets `204 No Content` and no body, so the header keeps the last count rather than showing a sign-in page.

## Replace a template or component

Any template or component named below can be replaced by putting a file of the same name in your project's templates, as described in the README's section on overriding a template.

| Name | What it draws |
|---|---|
| `cotton/mvp_community/notifications/bell.html` | The bell and its count, `<c-mvp_community.notifications.bell />` |
| `cotton/mvp_community/notifications/item.html` | One row of the notifications page, `<c-mvp_community.notifications.item />` |
| `cotton/mvp_community/notifications/preferences_card.html` | The Account Center card, `<c-mvp_community.notifications.preferences_card />` |
| `mvp_community/notifications/list.html` | The notifications page |
| `mvp_community/notifications/preferences.html` | The preferences page |
| `mvp_community/notifications/bell_partial.html` | What the `bell` route returns |
| `mvp/account/overview.html` | The Account Center landing page, which places the card |
| `notifications/email/realtime/message.html`, `message.txt`, `subject.txt` | One notification email: its HTML part, plain text part and subject |
| `notifications/email/realtime/<type key>.html`, `<type key>.txt`, `<type key>_subject.txt` | The same three for one notification type only, found before the general ones |
| `notifications/email/digest/message.html`, `message.txt`, `subject.txt` | A daily or weekly digest. The subject switches on `frequency.key` |
| `notifications/email/unsubscribe_footer.html` | The footer both kinds of email include |

Replacing one leaves the rest of the feature as it was.

## Pages and routes

Each route has a name in the `mvp_community_notifications` namespace. The preferences page belongs to the Account Center, so it sits under `account/`, the address django-mvp's URLs give the Account Center.

| Name | Address | View | What it does |
|---|---|---|---|
| `list` | `notifications/` | `NotificationListView` | The signed-in person's notifications, newest first, 20 to a page. |
| `open` | `notifications/<int:pk>/` | `OpenNotificationView` | Marks one of their notifications read and redirects to its `url`, or to the list when it has none or points at another site. Another person's notification is a 404. |
| `mark_all_read` | `notifications/read/` | `MarkAllReadView` | POST only. Marks every unread notification on the site as read, and redirects to the list. A notification sent only by email stays unread. |
| `bell` | `notifications/bell/` | `BellView` | The bell alone, for its own refresh. |
| `preferences` | `account/notifications/` | `PreferencesView` | GET shows the grid of types, channels and email frequencies. POST saves it, adds a success message and redirects back. |
| `unsubscribe` | `notifications/unsubscribe/<str:token>/` | `UnsubscribeView` | GET asks to confirm. POST turns email off for the types the link names. Open to a signed-out visitor. |

The views live in `mvp_community.integrations.notifications.views`. To change one, subclass it and route your subclass at the same address ahead of the include.

Every route except `bell` and `unsubscribe` redirects a signed-out visitor to your sign-in page. `bell` answers a signed-out request with an empty 204 response, so the bell keeps its last count instead of drawing a sign-in page in the header.

## Template tag

`notifications_unread_count` returns the signed-in person's unread notifications on the site, or `None` for a signed-out visitor. It reads `request.user` from the template context, so the `request` context processor must be enabled.

```django
{% load mvp_community_notifications %}
{% notifications_unread_count as count %}
```

## Why the count only includes the site

A notification can reach a person on several channels. The bell and the notifications page show what arrived on the site, so a notification sent only by email is not counted and is not marked read by "Mark all read". Marking it read would stop django-generic-notifications including it in an email digest.
