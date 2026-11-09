# Push

Push delivers a notification to a person's browser as it happens, even when the site is closed. It is built on [django-push-notifications](https://github.com/jazzband/django-push-notifications), which stores each browser's subscription and talks to the browser vendors' push services, and [py-vapid](https://github.com/web-push-libs/vapid), which signs what the server sends. This package supplies the channel that sends, a card on the notification preferences page where a person turns push on and sees which of their browsers receive it, and the service worker that shows a push when it arrives.

Push is a channel of [Notifications](notifications.md), so install that first. Declaring notification types and sending notifications work as described there. This page covers what you add to use push.

## Install push

Install the extra, add the app, set the signing key, include the URLs and create the tables.

1. Install the `push` extra. It brings the notifications packages with it:

   ```bash
   pip install "django-mvp-community[push]"
   ```

2. Add `push_notifications` to `INSTALLED_APPS`, beside the apps the notifications extra needs:

   ```python
   INSTALLED_APPS = [
       # ...
       "generic_notifications",
       "push_notifications",
   ]
   ```

3. Generate the key pair the server signs push with. `vapid` comes with py-vapid, so it is installed already:

   ```bash
   vapid --gen
   ```

   It writes `private_key.pem` and `public_key.pem` to the current directory. Keep the private key out of version control and out of your settings file's text: store it as a file your deployment provides, or in the environment.

4. Name the key and a contact in `PUSH_NOTIFICATIONS_SETTINGS`. `WP_PRIVATE_KEY` is the path to the private key file, or the key itself as a URL-safe base64 string. `WP_CLAIMS` must carry a `sub`, a `mailto:` or `https:` address the push services can reach if your server misbehaves:

   ```python
   import os

   PUSH_NOTIFICATIONS_SETTINGS = {
       "WP_PRIVATE_KEY": os.environ["PUSH_PRIVATE_KEY_PATH"],
       "WP_CLAIMS": {"sub": "mailto:admin@example.com"},
   }
   ```

5. Include the push URLs at the root, beside the notifications URLs. Their routes are listed under [Pages and routes](#pages-and-routes):

   ```python
   from django.urls import include, path

   urlpatterns = [
       # ...
       path("", include("mvp_community.integrations.notifications.urls")),
       path("", include("mvp_community.integrations.push.urls")),
   ]
   ```

6. Create django-push-notifications' tables:

   ```bash
   python manage.py migrate
   ```

Starting the project registers the push channel when both `generic_notifications` and `push_notifications` are installed. Without `push_notifications` nothing is registered, the preferences page has no push column and no push card, and the page is unchanged.

Push needs HTTPS. Browsers refuse to subscribe on a page served over plain HTTP, except on `localhost`.

## Send notifications by push

Name the package's channel wherever a notification type lists channels, as you do for email:

```python
from generic_notifications.types import NotificationType, register

from mvp_community.integrations.push.channels import PushChannel


@register
class SecurityNotice(NotificationType):
    key = "security_notice"
    name = "Security notices"
    description = "Sign-ins from a new device and changes to your account"
    required_channels = [PushChannel]
```

A type that does not list `PushChannel` is still offered on push: the preferences page draws a push column for every type, as it draws one for every channel, and a person turns push on for the types they want. Name the channel in `required_channels` only for a type that must always arrive, or in `forbidden_channels` for one that must never be pushed.

A notification is pushed to every browser of its recipient that has push turned on, at the moment it is created. Push has no digest: a type a person receives as a daily email digest is still pushed at once. A person with push off for the type gets nothing.

What each push shows is the notification's subject as the title, its text as the body, cut to 400 characters, an icon, and a link that opens the notification on the site, which marks it read on the way.

The icon is the first of these that is set:

1. The notification type's `push_icon`, for a type with an icon of its own.
2. The `MVP_COMMUNITY_PUSH_ICON` setting, the icon for every other push.
3. The site's own icon, from django-mvp's brand icon resolver.

Each is a static path, such as `"brand/push-icon.png"`, or a URL. It is sent as an absolute address, built from the same base URL django-generic-notifications uses for a notification's link. With none of the three, the push shows no icon. Some browsers draw no SVG icon on a push, so set a square PNG of at least 192 pixels:

```python
MVP_COMMUNITY_PUSH_ICON = "brand/push-icon.png"


@register
class ReplyReceived(NotificationType):
    key = "reply_received"
    name = "Replies"
    push_icon = "brand/reply-icon.png"
```

A push service that is slow, refuses the message or no longer knows the browser does not stop the others or fail the code that sent the notification. `PushChannel` writes each failure to the `logger` of `mvp_community.integrations.push.channels` at warning level, and goes on to the person's next browser. A browser the push service reports as gone is retired by django-push-notifications.

## The preferences page

The push card sits above the table on the notification preferences page. It has a button that turns push on for the browser being used, which asks the browser's permission; a list of the browsers that receive push, each with the day it was turned on and a Stop button; and a message in its place when the browser cannot receive push or the person blocked notifications from the site. A browser's name and icon are read from the user agent it subscribed with.

The card is the Cotton component `mvp_community.notifications.push_card`, and the page draws it only when the push channel is registered. It draws these icon names, which you register in `EASY_ICONS` as you do the notification icons:

| Icon name | Used for |
|---|---|
| `notifications.push` | The card's heading |
| `notifications.push.phone` | A browser on an iPhone or Android phone |
| `notifications.push.tablet` | A browser on an iPad |
| `notifications.push.computer` | Any other browser |

Stopping a browser from the list deletes its subscription. It does not touch the subscription inside the browser itself, because two people can share one browser and it holds a single subscription for both. After a person stops the browser they are using, the card offers to turn push on again.

On an iPhone or iPad, push reaches a site only once it is added to the Home Screen and opened from there, so the card says so instead of offering the button in an ordinary Safari tab.

## Pages and routes

The push routes are included at the root, with the namespace `mvp_community_push`:

| Name | Address | Purpose |
|---|---|---|
| `worker` | `notifications/push/worker.js` | The service worker. Served signed out, with a JavaScript content type, and revalidated on each load. |
| `subscribe` | `notifications/push/subscribe/` | Stores a browser's subscription for the signed-in person and sends a test push. |
| `stop` | `notifications/push/<pk>/stop/` | Deletes one of the signed-in person's own subscriptions. |

The views behind the routes are `WorkerView`, `SubscribeView` and `StopView` in `mvp_community.integrations.push.views`. `SubscribeView` reads the JSON a browser's push manager produces and answers 204, or 400 with nothing stored when the endpoint, the `p256dh` key or the `auth` secret is missing or malformed. The key must decode to 65 bytes and the secret to 16. When the browser had to drop a subscription made with an earlier key, it sends that endpoint as `previous`, and the person's row for it is deleted. A person keeps at most `SUBSCRIPTION_LIMIT` subscriptions, 20, since every notification is sent to each of them: storing one more deletes their oldest. It accepts an endpoint only when `is_push_endpoint` in `mvp_community.integrations.push.subscriptions` says it is on a push service the major browsers use: `fcm.googleapis.com`, `updates.push.services.mozilla.com`, `web.push.apple.com`, or a host ending in `.notify.windows.com` or `.push.apple.com`. An endpoint longer than 1024 characters, or whose host is anything but a plain DNS name, is refused as well. Anything else is refused, so a signed-in person cannot make your server post to an address of their choosing.

`Browser.from_user_agent` in the same module reads a browser's `family`, `place` and `kind` (`phone`, `tablet` or `computer`) from a user agent string, and its `label` is the translated name, such as "Chrome on Android".

## Check your settings

Starting the project runs the system check `mvp_community.E002`, which reports a missing or empty `WP_PRIVATE_KEY`, and `WP_CLAIMS` that are missing or have no `sub`. Each is reported as its own error naming the setting.

Production servers usually do not run system checks on start. Run `python manage.py check --deploy` before you release, or a missing key shows first as an error on the preferences page.

## Replace the key pair

A subscription is tied to the key that was current when the browser subscribed. Push services refuse a message signed with a different key, so replacing `WP_PRIVATE_KEY` retires every existing subscription at once. People keep their other channels. On their next visit the preferences page offers to turn push on again in each browser, and turning it on replaces the browser's old subscription and removes it from their list. Replace the key only when you have to, such as after it leaks.

## Write push in the person's language

Each push is written in the language `PushChannel.recipient_language(user)` returns. Django stores no language per person, so the default is the site's `LANGUAGE_CODE`. A project that stores one subclasses the channel and returns it:

```python
from mvp_community.integrations.push.channels import PushChannel


class ProfileLanguageChannel(PushChannel):
    def recipient_language(self, user):
        return user.profile.language
```

Register the subclass from `AppConfig.ready()`, after the push extra has started, with `registry.register_channel(ProfileLanguageChannel, force=True)`. Name the subclass, not `PushChannel`, in a type's channels, because django-generic-notifications compares channels by identity.

## Use your own service worker

The card registers a service worker of its own, served from the `worker` route. Its scope is the address it is served from, so it does not take over the site's pages, and a worker your project registers at the site root is not replaced.

To change what the worker does, ship a template named `mvp_community/push/worker.js` in your project. It replaces the package's, as any template of the package can be replaced, and has to handle the `push` event and the `notificationclick` event itself. To change the card, ship a Cotton component named `mvp_community/notifications/push_card.html` in the same way. The card's context is built by `card_context` in `mvp_community.integrations.push.subscriptions`: the person's active `subscriptions`, newest first, each with a `reader`, the `Browser` read from its stored user agent, `just_turned_on` (true once, on the page shown after push was turned on), the `application_server_key` the browser subscribes with, and the `worker_url` and `subscribe_url` the card's script uses.
