# Sketch: Activity feeds and following

## What exists

- **Data.** django-activity-stream supplies everything the screens read. An action has an actor, a verb, an optional action object and target, a description, a timestamp and a public flag. A follow joins a person to any registered object, either for what it does alone or for everything around it. Deleting an object removes its follows and, through the generic relations the package adds to each registered model, its actions.
- **What the package already does.** Its manager gives the public actions, the actions around one object (`any`), the actions of what a person follows (`user`), and filters any of them by keyword, such as `verb`. It has queries for an object's followers and for what a person follows. Its URLs follow and stop following by POST, return to `next`, and require a signed-in person. Its template tags put any stream into the context (`activity_stream`), say whether a person follows something (`is_following`) and give the follow or stop-following address (`follow_url`, `follow_all_url`).
- **What it lacks.** Its own pages are bare and unpaginated, and it has no tag for an object's followers.
- **The shell.** The feed page is a list page in the application shell with an entry in the sidebar. The following page is an Account Center page with an entry in `AccountCenterMenu` and a card in `account.cards`, the way the notification preferences page is added. htmx is bundled, so the follow control posts without leaving the page.
- **Components.** daisy-cotton's `list`, `list.row`, `avatar`, `badge`, `link` and `button`, and django-mvp's `card`, `page.side`, `page.list.empty`, `page.list.footer`, `section` and Account Center page.
- **Planning notes.** Both are applied. The feature depends on django-activity-stream alone, which installs and runs on Django 6.1. Its own views, URLs, queries and template tags are used wherever they exist, and the one template tag written here, `followers_of`, gives templates a query the package has no tag for.

## What the screens need from the code

- The feed page needs one page of the signed-in person's stream, newest first.
- The following page needs one page of the signed-in person's follows, newest first, each with what is followed and its kind.
- The follow control and the followers list need an object's followers, which no django-activity-stream tag gives a template.
- The follow control posts to django-activity-stream's own follow and stop-following addresses, so a host project includes its URLs.
- Every name in a row links through `get_absolute_url`, so a person or object without one shows as plain text.
- Every model that acts, is acted on or is followed is registered with django-activity-stream's registry.
- Recent activity needs the stream's total, to decide whether to show the link to the full list.

## What the sketch faked

- The people and groups are Django's own users and groups, registered with django-activity-stream in the demo's app config. Their pages, and the addresses `ABSOLUTE_URL_OVERRIDES` gives them, exist only in the demo.
- Every action comes from `seed_activity`, written straight into the database rather than recorded where something happened.
- django-activity-stream's URLs are included by the demo at `activity/`, after this package's feed page.
- The icons `activity`, `activity.follow`, `activity.following` and `people` are registered in the demo's settings.
- Avatars show initials. Nothing resolves a photo.
- The overview page's three recent-activity cards and the "People and groups" page exist only to show the components. The icon `activity.unfollow` is registered in the demo's settings.

## What was ruled by eye

- Every page is built from django-mvp and daisy-cotton components and the classes django-mvp's stylesheet already ships, with no styles of its own.
- The follow control is the follower count as plain text beside one button that names what it does: Follow (primary) or Unfollow (outline). Sam, round 1: a count inside a button labelled Following read as a menu of followers, and clicking it unfollowed him. On a person's own page it is the count alone.
- An activity row is the actor's avatar, one sentence with each name linked, the description under it when there is one, and how long ago.
- On a person's or an object's page the follow control sits in the title row, and the followers list is a column beside its recent activity, showing the first eight and how many more.
- Following an object follows everything around it: what it does, what is done to it and what happens in it.
- The feed page's title row has a labelled button to the following page.
- Names in a row are bold and linked, and the verb between them is plain, so a sentence reads as who did what to what.
- Avatars are the stylesheet's `size-10` (`size-8` in the followers list). `w-10` and `h-10` are not in django-mvp's stylesheet.
- The followers list carries no heading of its own beside a page that already names it (`plain`).
- Recent activity is one component for the whole site, one object or what a person follows. The developer chooses how many it shows (default ten) and may give the full list's address, linked at its foot as "View all activity" when there is more. It is never paged. Sam, round 1.
