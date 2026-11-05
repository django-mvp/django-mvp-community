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

## What django-generic-notifications adds by itself

Installing django-generic-notifications registers an Email channel and a "System Message" notification type. Both appear on the preferences page in every project, and System Message notifications are always sent by email. Email notifications are sent through Django's own email settings, so configure `EMAIL_BACKEND` before sending any.

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

Every registered type is listed on the preferences page against every channel. A channel the type requires is drawn on and cannot be turned off. A channel it forbids is drawn as unavailable.

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

Replacing one leaves the rest of the feature as it was.

## Pages and routes

Each route has a name in the `mvp_community_notifications` namespace.

| Name | Address | View | What it does |
|---|---|---|---|
| `list` | `notifications/` | `NotificationListView` | The signed-in person's notifications, newest first, 20 to a page. |
| `open` | `notifications/<int:pk>/` | `OpenNotificationView` | Marks one of their notifications read and redirects to its `url`, or to the list when it has none or points at another site. Another person's notification is a 404. |
| `mark_all_read` | `notifications/read/` | `MarkAllReadView` | POST only. Marks every unread notification on the site as read, and redirects to the list. A notification sent only by email stays unread. |
| `bell` | `notifications/bell/` | `BellView` | The bell alone, for its own refresh. |
| `preferences` | `account-center/notifications/` | `PreferencesView` | GET shows the grid of types and channels. POST saves it, adds a success message and redirects back. |

The views live in `mvp_community.integrations.notifications.views`. To change one, subclass it and route your subclass at the same address ahead of the include.

Every route except `bell` redirects a signed-out visitor to your sign-in page. `bell` answers a signed-out request with an empty 204 response, so the bell keeps its last count instead of drawing a sign-in page in the header.

## Template tag

`notifications_unread_count` returns the signed-in person's unread notifications on the site, or `None` for a signed-out visitor. It reads `request.user` from the template context, so the `request` context processor must be enabled.

```django
{% load mvp_community_notifications %}
{% notifications_unread_count as count %}
```

## Why the count only includes the site

A notification can reach a person on several channels. The bell and the notifications page show what arrived on the site, so a notification sent only by email is not counted and is not marked read by "Mark all read". Marking it read would stop django-generic-notifications including it in an email digest.

## Why saving preferences clears digest frequencies

django-generic-notifications' `save_notification_preferences` replaces every saved choice with the ones posted, including any digest frequency. The preferences page posts channel choices only, so a person who has a digest frequency set elsewhere loses it when they save. No digest feature is built on this page yet.
