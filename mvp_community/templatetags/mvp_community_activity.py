"""The one thing django-activity-stream's own tags do not give a template."""

from django import template

register = template.Library()


@register.simple_tag
def followers_of(obj):
    """Return the people who follow ``obj``.

    django-activity-stream has a ``followers`` query and no tag for it. The
    import sits inside the tag so the base install never loads the extra.

    Args:
        obj: The person or object whose followers are wanted.

    Returns:
        A queryset of the people following it, so ``.count`` is one query.
    """
    from actstream.models import followers

    return followers(obj)
