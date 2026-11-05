# Research: Notifications on the site

## Planning notes

### "The packages worth looking at have already been determined"

**Adopted.** The package's brainstorm names django-generic-notifications for the notifications extra, and the sketch is built on it. Version 2.4.0 supplies everything the three stories read and write:

- `Notification`, with `read` as a timestamp, `url`, `subject` and `text`, and the queryset helpers `unread()` and `for_channel()`.
- `generic_notifications.utils`: `get_unread_count(user)`, `get_notifications(user)` and `mark_notifications_as_read(user)`, The first two are scoped to the site channel by default. `mark_notifications_as_read` is not: it marks every channel's notifications read, so the plan does not use it.
- `Notification.mark_as_read()`.
- `generic_notifications.preferences`: `get_notification_preferences(user)`, which returns the type-by-channel grid with each choice and whether it is required or forbidden, and `save_notification_preferences(user, data)`, which saves the grid from form fields named `<type>__<channel>`.
- A registry of types and channels. The package registers the site and email channels and a "System Message" type on its own.

No other package is needed for these stories.

## The sketch

Every line under "What the screens need from the code" in `sketch.md` is met by the package's functions above, wired by four small views and one template tag. Every line under "What the sketch faked" becomes a task or a documentation item in `tasks.md`.

## Decisions settled here

- **How the extra is switched on.** The host project installs the extra, adds `generic_notifications` and `django.contrib.humanize` to `INSTALLED_APPS`, includes `mvp_community.integrations.notifications.urls` at the root, and names `mvp_community.notifications.bell` in `MVP_CONFIG["layout"]["navbar"]["end"]`. The last of those is how django-mvp places every header widget, so the package cannot place it itself. The icon names `notifications` and `notifications.preferences` are mapped in the project's `EASY_ICONS`, as django-mvp-accounts asks for its own. See D1 in `decisions.md`.
- **The unread count reaches the bell through a template tag, not a context processor.** A context processor would be one more setting. The tag library `mvp_community_notifications` lives in `mvp_community/templatetags/` because Django only finds tag libraries there, and it imports nothing from the extra at module level: the tag calls into the integration module when it runs. The base-install test imports the tag library with the extra blocked, so a module-level import fails the suite. See D2.
- **The Account Center entry** is registered from `MvpCommunityConfig.ready()` when `generic_notifications` is installed, by importing the integration module's `menus`. django-mvp drops an entry whose URL does not resolve, so a project that installed the package but not the URLs shows nothing.
- **Routes.** The URLconf places its own routes, as `mvp.urls` does: `notifications/` for the list, the bell's refresh, opening one and marking all read, and `account-center/notifications/` for preferences, as Sam ruled at the sketch gate.
- **Times** use `naturaltime` from `django.contrib.humanize`, which Django ships.

## What already exists

| New piece | Where the search stopped |
|---|---|
| Unread count | installed package: `generic_notifications.utils.get_unread_count` |
| One person's notifications, newest first | installed package: `get_notifications`, model ordering `-added` |
| Mark all read | installed package: `get_notifications(user, unread_only=True)`, then a queryset `update` |
| Mark one read | installed package: `Notification.mark_as_read` |
| Preferences grid and saving it | installed package: `get_notification_preferences`, `save_notification_preferences` |
| Page context, sign-in, pagination | django-mvp `MVPListView` and `MVPTemplateView` with Django's `LoginRequiredMixin`; display: `c-mvp.page.list.footer` |
| Empty state | django-mvp `c-mvp.page.list.empty` |
| List rows, dot, table, toggle, indicator, button | daisy-cotton components |
| Account Center page, menu and card | django-mvp `mvp/account/base.html`, `AccountCenterMenu`, `account.cards` block |
| Relative times | Django: `django.contrib.humanize` `naturaltime` |
| Polling | htmx, bundled with django-mvp |
| Signed-in guard | Django: `LoginRequiredMixin` |
| Four views and one template tag | new code: the wiring between the package and the pages |
