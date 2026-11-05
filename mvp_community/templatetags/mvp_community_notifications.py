"""Template tags for the notifications extra."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def notifications_unread_count(context):
    """Count the signed-in person's unread notifications on the site.

    django-generic-notifications is imported inside the tag, not at the top of
    the module, because Django only finds a tag library under this package's
    ``templatetags`` and a project installed without the extra still loads it.

    Args:
        context: The template context, which carries the request.

    Returns:
        The unread count, or None for a signed-out visitor or a context
        with no request.
    """
    request = context.get("request")
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return None

    from generic_notifications.utils import get_unread_count

    return get_unread_count(user)
