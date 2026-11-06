"""What django-activity-stream's own tags do not give a template."""

from urllib.parse import urlencode

from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

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


@register.simple_tag
def followed_activity(user, verb=""):
    """Return the feed of what ``user`` follows, as the feed view shows it.

    Args:
        user: The signed-in person.
        verb: When given, only activity of this kind.

    Returns:
        The public activity of what they follow, without their own actions.
    """
    from mvp_community.integrations.activity.streams import (
        followed_activity as stream,
    )

    return stream(user, **({"verb": verb} if verb else {}))


@register.simple_tag
def follow_control_url(obj, page=""):
    """Return the address that draws ``obj``'s follow control on its own.

    Args:
        obj: The person or object the control belongs to.
        page: The page the control sits on, which its plain form returns to.

    Returns:
        The address of the follow control route, carrying ``page`` as ``next`` when given.
    """
    address = reverse(
        "mvp_community_activity:follow_control",
        args=[ContentType.objects.get_for_model(obj).pk, obj.pk],
    )
    return f"{address}?{urlencode({'next': page})}" if page else address
