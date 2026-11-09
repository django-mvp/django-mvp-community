# Activity

Activity gives a django-mvp project a following page in the Account Center, a feed view you mount wherever you want a feed, and components to place on your own pages: recent activity, a follow control and a followers list. It is built on [django-activity-stream](https://django-activity-stream.readthedocs.io/), which records activity, stores follows and decides what a person sees. This package supplies the pages and components around it. It adds no models and no migrations of its own.

Recording activity is done with django-activity-stream, as described in its own documentation. This page covers what you add to a project to show it.

## Install activity

Install the extra, add two apps, register your models, add one icon set and include the URLs.

1. Install the `activity` extra:

   ```bash
   pip install "django-mvp-community[activity]"
   ```

2. Add `actstream` and `django.contrib.humanize` to `INSTALLED_APPS`, after `mvp_community`, which sits above `mvp` so its Account Center card is used. A row says when something happened as "2 hours ago", which `humanize` supplies:

   ```python
   INSTALLED_APPS = [
       # ...
       "mvp_community",
       "mvp",
       "actstream",
       "django.contrib.humanize",
   ]
   ```

3. Keep `django.template.context_processors.request` and `django.contrib.auth.context_processors.auth` in your template context processors. The components read `request.user` to tell a signed-in person from a visitor.

4. Register the icons the components draw, `activity`, `activity.follow`, `activity.unfollow` and `activity.following`, in your `EASY_ICONS` setting. An icon name that is not registered raises an error rather than drawing nothing:

   ```python
   EASY_ICONS = {
       "default": {
           # ...
           "icons": {
               "activity": "bi bi-activity",
               "activity.follow": "bi bi-plus-lg",
               "activity.unfollow": "bi bi-x-lg",
               "activity.following": "bi bi-check2",
           },
       },
   }
   ```

5. Include the URLs at the root of your site, beside `mvp.urls`:

   ```python
   urlpatterns = [
       # ...
       path("", include("mvp_community.integrations.activity.urls")),
       path("", include("mvp.urls")),
   ]
   ```

6. Create django-activity-stream's tables:

   ```bash
   python manage.py migrate
   ```

Signed in, the Account Center now has a Following entry and a card. No feed exists yet: you mount one, as described under [Mount a feed](#mount-a-feed).

## Register the models that take part

Only a registered model can act, be acted on or be followed. Register each one with django-activity-stream's `registry`, in a module your app imports when it starts, such as from `AppConfig.ready()`:

```python
from actstream import registry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

registry.register(get_user_model(), Group)
```

## Record activity

Record each thing that happens with django-activity-stream's `action.send`:

```python
from actstream import action

action.send(request.user, verb="finished", target=lesson, public=True)
```

A feed and recent activity show activity recorded as public, which is the default. Activity recorded with `public=False` appears in no feed. Hiding activity about an object from people who may not see it is your project's decision: record it as not public.

Activity whose actor, target or action object has since been deleted is not shown.

## Link names to pages

A name in a row links to the page of the person or object when the model has a `get_absolute_url`, and is plain text otherwise. For a model you do not control, name its page in `ABSOLUTE_URL_OVERRIDES`:

```python
ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda user: f"/people/{user.pk}/",
}
```

A person is named by their full name, or by how your project names them when they have none.

## Mount a feed

A feed is a view you mount at an address of your choosing. `ActivityFeedView` lists public activity newest first, 20 to a page, and takes three settings, as class attributes or as arguments to `as_view()`:

| Setting | What it does |
|---|---|
| `stream` | `"following"` (the default) for the public activity of what the signed-in person follows, `"site"` for the public activity of the whole site, or `"object"` for the public activity around one object. |
| `verb` | When set, limits the feed to activity of that kind, such as `"finished"`. |
| `get_stream_object()` | A method that returns the object an `"object"` feed is about. The default raises `ImproperlyConfigured`. |

A following feed never lists the person's own activity, which includes the "started following" activity that following someone records. A signed-out visitor is sent to sign in. The other two streams are open to everyone.

Mount the feed of what a person follows, a feed of the whole site, and a feed of one kind of activity:

```python
from mvp_community.integrations.activity.views import ActivityFeedView

urlpatterns = [
    path("activity/", ActivityFeedView.as_view(), name="activity"),
    path("activity/site/", ActivityFeedView.as_view(stream="site"), name="site_activity"),
    path(
        "activity/finished/",
        ActivityFeedView.as_view(stream="site", verb="finished"),
        name="activity_finished",
    ),
]
```

Mount a feed around one object by subclassing the view and returning the object from the address:

```python
class LessonActivityView(ActivityFeedView):
    stream = "object"

    def get_stream_object(self):
        return get_object_or_404(Lesson, pk=self.kwargs["pk"])


urlpatterns = [
    path("lessons/<int:pk>/activity/", LessonActivityView.as_view(), name="lesson_activity"),
]
```

The page title and lead are set the way any django-mvp list view sets them, with `page_title` and `page_lead`. The title reads "Activity" by default.

Add a feed to your sidebar with a menu entry for its route:

```python
from flex_menu import MenuItem
from mvp.menus import AppMenu

AppMenu.append(
    MenuItem(
        name="activity",
        view_name="activity",
        extra_context={"label": "Activity", "icon": "activity"},
    )
)
```

## Place recent activity on a page

Recent activity is the newest few activities in a card, for a dashboard or any page. It is never split into pages.

```django
<c-mvp_community.activity.recent limit="5" more_url="/activity/" />
<c-mvp_community.activity.recent :object="lesson" verb="finished" />
<c-mvp_community.activity.recent following />
```

| Prop | What it does |
|---|---|
| `object` | Shows the public activity around this person or object. Without it, the whole site's. |
| `following` | Shows what the signed-in person follows. A signed-out visitor sees the empty state. |
| `verb` | Shows only activity of this kind. |
| `limit` | How many of the newest to show. Default 10. |
| `more_url` | Where the full list lives. When given and there is more than `limit` shows, a link to it appears at the foot. |
| `more_text` | The link's text. Default "View all activity". |

## Place a followers list on a page

The followers list is a card headed with how many people follow a person or an object. It lists the first eight and says how many more.

```django
<c-mvp_community.activity.followers :object="lesson" />
<c-mvp_community.activity.followers :object="lesson" plain />
```

`plain` leaves out the heading, for a page that already names the list.

## Place a follow control on a page

The follow control shows how many people follow a person or an object beside a Follow button, which becomes Unfollow once the signed-in person follows. A signed-out visitor gets a link to sign in. A person's own control has the count and no button.

```django
<c-mvp_community.activity.follow :object="lesson" />
<c-mvp_community.activity.follow :object="lesson" size="md" />
<c-mvp_community.activity.follow :object="lesson" next="/lessons/" />
```

| Prop | Meaning |
|---|---|
| `object` | The person or object to follow. It must be registered with django-activity-stream. |
| `size` | `xs`, `sm` or `md`: the button's size. |
| `next` | The page the control sits on. A plain form post and signing in return to it. It defaults to the current page. |
| `replace_row` | Set it when the control sits in a list row that carries `data-follow-row`. Stopping following then removes that row instead of redrawing the control. The following page uses it. |

Clicking posts to django-activity-stream's follow address with htmx, and only the control is redrawn: the button changes between Follow and Unfollow and the count changes with it. The control is the element marked `data-follow-control`. Without htmx the form posts normally and returns to `next`.

The control needs htmx on the page, which django-mvp's base template loads.

`size` is `xs`, `sm` or `md`, and sets the button's size.

## Count followers in your own template

`followers_of` returns the people who follow an object as a queryset, so `.count` is one query:

```django
{% load mvp_community_activity %}
{% followers_of lesson as people %}
{{ people.count }}
```

## Read the feed of what someone follows in your own template

`followed_activity` returns the same activity a feed set to `following` shows: the public activity of what a person follows, newest first, without their own actions. Give it a kind to limit it:

```django
{% load mvp_community_activity %}
{% followed_activity request.user "finished" as actions %}
{% for action in actions|slice:":5" %}{{ action }}{% endfor %}
```

## Replace a template or component

Any template or component named below can be replaced by putting a file of the same name in your project's templates, as described in the README's section on overriding a template.

| Name | What it draws |
|---|---|
| `cotton/mvp_community/activity/recent.html` | Recent activity, `<c-mvp_community.activity.recent />` |
| `cotton/mvp_community/activity/feed.html` | A card of rows, or the empty state, `<c-mvp_community.activity.feed />` |
| `cotton/mvp_community/activity/entry.html` | One row: who did what, to what, and when, `<c-mvp_community.activity.entry />` |
| `cotton/mvp_community/activity/name.html` | The name of a person or an object, linked where it has a page, `<c-mvp_community.activity.name />` |
| `cotton/mvp_community/activity/follow.html` | The follow control, `<c-mvp_community.activity.follow />` |
| `cotton/mvp_community/activity/followers.html` | The followers list, `<c-mvp_community.activity.followers />` |
| `cotton/mvp_community/activity/following_card.html` | The Account Center card, `<c-mvp_community.activity.following_card />` |
| `mvp_community/activity/follow_control.html` | The follow control on its own, which htmx fetches after a click |
| `mvp_community/activity/feed.html` | The page `ActivityFeedView` draws |
| `mvp_community/activity/following.html` | The following page |
| `mvp/account/overview.html` | The Account Center landing page, which places the card |

Replacing one leaves the rest of the feature as it was.

## Pages and routes

The following page is in the `mvp_community_activity` namespace. django-activity-stream's follow routes keep their own names, with no namespace, because its template tags look them up by those names. The following page belongs to the Account Center, so it sits under `account/`, the address django-mvp's URLs give the Account Center.

| Name | Address | What it does |
|---|---|---|
| `mvp_community_activity:following` | `account/following/` | `FollowingView`: the signed-in person's follows, newest first, 20 to a page. A signed-out visitor is sent to sign in. |
| `mvp_community_activity:follow_control` | `activity/control/<content_type_id>/<object_id>/` | `FollowControlView`: draws one object's follow control alone. A signed-out visitor is sent to sign in, and a model not registered with django-activity-stream is not found. Its `next` parameter is used when it is an address on your site. |
| `actstream_follow` | `activity/follow/<content_type_id>/<object_id>/` | Follows the object, recording what it does. |
| `actstream_follow_all` | `activity/follow_all/<content_type_id>/<object_id>/` | Follows the object, recording what it does and what happens to it. |
| `actstream_unfollow` | `activity/unfollow/<content_type_id>/<object_id>/` | Stops following the object. |
| `actstream_unfollow_all` | `activity/unfollow_all/<content_type_id>/<object_id>/` | Stops following the object, in both senses. |

The view lives in `mvp_community.integrations.activity.views`. To change it, subclass it and route your subclass at the same address ahead of the include.

## Why the package mounts no feed

Where a feed lives and what it shows is your project's decision, so the package ships the view and leaves the address, the menu entry and the title to you. The following page is built in because it has nothing a project would change.

## Why only the follow routes are mounted

django-activity-stream's own URLconf also mounts a page showing any activity by its number, including activity that is not public, and a page listing anyone's follows to anyone. This package mounts the four follow routes only, taken from that URLconf by name, so neither page exists in your project.

## Known limits of django-activity-stream's follow routes

The follow routes are django-activity-stream's own views, and this package does not change their behaviour:

- They do not check a CSRF token. The follow control sends one anyway.
- They follow on a plain GET request as well as a POST.
- They redirect to any `next` address without checking it.
- Following records a public "started following" activity.

django-activity-stream can also tag a follow with a flag, such as `liking` or `watching`. This package draws no flags: a flagged follow counts as an ordinary follow in every count and list, and Unfollow removes it.

A page with many follow controls asks the database a few questions for each one.
