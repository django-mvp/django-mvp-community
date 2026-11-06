# Research — 002 Activity feeds and following

Against `main` of 2026-11-06, with django-activity-stream 2.0.0 installed in the branch's environment.

## Planning notes

- **"This particular depends only on django-activity-stream."** Adopted. The `activity` extra is `django-activity-stream>=2.0`. Version 2.0.0 installs, migrates and runs on Django 6.1.3 (the lock file's), and declares `Django>=3.2` with no upper bound. CI's Django matrix (5.2, 6.0, 6.1) is the proof for the other two.
- **"We AVOID writing custom code where possible ... template tags are allowed but ... django-activity-stream already provides its own."** Adopted. Every read and write is django-activity-stream's: its manager's `public`, `any` and `user` streams, `Follow.objects.followers_qs`, `following_qs` and `is_following`, its `follow`/`unfollow` views and URLs, and its `activity_stream`, `is_following` and `follow_all_url` tags. What is written here is listed under *What already exists*, each with the reason the package's own does not do it.
- **Count followers with a database `COUNT`.** Adopted. `Follow.objects.followers_qs(obj).count()`. The sketch's `followers(obj)|length` loaded every follower's user row.
- **The follow control swaps only itself.** Adopted. The control posts to django-activity-stream's own follow or stop-following address with htmx, and that view's `next` redirect points at a read-only route that renders the control again. htmx follows the redirect and swaps the control in place. No follow logic is written here, and the route only renders. The plain form post, redirecting back to the page, is the fallback without JavaScript.
- **Counts and "do I follow this" for a whole page in two queries: left out** unless a real project's list is slow, and noted in the documentation.

## What the sketch needs and faked

| From `sketch.md` | Met by |
|---|---|
| The feed page: one page of the person's stream | `FeedView` over `Action.objects.user(request.user)`, which is a stream and already fetches its generic relations |
| The following page: one page of follows with what is followed | `FollowingView` over `Follow.objects.following_qs(user)`, which fetches `follow_object` for the whole page in one pass, ordered newest first |
| An object's followers | `Follow.objects.followers_qs(obj)`, as a tag |
| The follow control posts to django-activity-stream's URLs | the host includes `actstream.urls` under `activity/`, documented |
| Names link through `get_absolute_url` | the `name` component; documented that a model without it shows plain text |
| Models are registered with django-activity-stream | the host's job; documented, with the registry call |
| Recent activity needs the stream's total | `count()` on the stream, one query |
| Fakes: the demo's people, groups, `ABSOLUTE_URL_OVERRIDES`, seeded actions, icons, URL include | they stay in the demo, which is never distributed. The icon names and the URL include are documented for a host project |

## What else was settled

- **Following an object follows everything around it.** `follow_all_url` posts to `follow_all`, which follows with `actor_only=False`, so the stream includes activity where the object is the target or the action object. That is what the spec's "activity about an object" means.
- **Deleted objects.** django-activity-stream deletes a deleted object's follows on `pre_delete`, and every registered model gains generic relations that cascade its actions. Nothing is written for FR-011's "no longer exists" half. Only public actions are read, which is the other half.
- **django-activity-stream's follow view is `csrf_exempt`**, upstream. A page on another site could make a signed-in person follow or stop following something. The control still sends the CSRF token. This is recorded as a known limitation in the documentation and not worked around.
- **Query cost in lists.** Each follow control costs a `COUNT` and an `exists()`, and `follow_all_url` runs `is_following` again internally: three queries per control. The following page therefore grows by three queries a row. Measured in the sketch: 128 queries for 40 rows on the demo's people page before the `COUNT` change.

## What already exists

| New piece | Stopped at | Found |
|---|---|---|
| Feed page view | 7, new code | `actstream.views.stream` renders the whole stream into a bare template with no pagination and no shell. A list view of ours gives `page_obj` and django-mvp's page context. The queryset is the package's own |
| Following page view | 7, new code | `actstream.views.following` takes a user id from the URL, shows any user's follows and is not paginated. Same reasoning |
| Control route (renders the follow control) | 7, new code | nothing renders one object's control alone. It calls no write |
| `follower_count` tag | 7, new code | `followers_qs` exists. No tag exposes it |
| `followers_of` tag | 7, new code | `followers()` exists. No tag exposes it |
| Recent activity, feed, action row, name, follow control, followers list, following card components | 2/3 for everything inside them | daisy-cotton's `list`, `list.row`, `avatar`, `badge`, `link`, `button`, django-mvp's `card`, `text`, `page.list.empty`, `page.list.footer`, `page.side`. The streams come from `{% activity_stream %}` |
| Sidebar and Account Center entries | 3 | `flex_menu.MenuItem` on `mvp.menus.AppMenu` and `AccountCenterMenu` |
| Account Center card placement | 2 | the package's existing `mvp/account/overview.html` override |
