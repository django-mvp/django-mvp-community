# Planning notes

The feature depends only on django-activity-stream. Sam, 2026-11-05: "This particular depends only on django-activity-stream I believe."

The project feature document that proposed this extra builds it on django-activity-stream "after a trial install on Django 6". This package supports Django 5.2, 6.0 and 6.1.

Sam, 2026-11-05, approving the specification: "Keep in mind that we are providing UI and templates for existing code. We AVOID writing custom code where possible. This follows Django-mvp philosophy and what happened in the notifications feature spec where custom code was rejected. If absolutely necessary, template tags are allowed but from memory Django-activity-feed already provides its own."

Sam, 2026-11-06, agreeing at the sketch gate to these from the list-performance answer (measured in the sketch: 128 queries for the 40-row people list, about three per follow control):

1. Count followers with a database `COUNT`, through django-activity-stream's own `followers_qs`, rather than loading every follower to count them.
2. The follow control swaps only itself: it posts with `hx-post` and replaces the control alone, through one small view that renders the control after calling django-activity-stream's own `follow`/`unfollow`. No follow logic of our own. The plain form post stays as the fallback without JavaScript.

Left out unless a real project's list is slow, and noted in the documentation: working out follower counts and "do I follow this" for a whole page in two queries.
